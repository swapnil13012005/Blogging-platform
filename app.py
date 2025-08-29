from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import markdown # For rendering markdown content
import os # Import os module to check for file existence

from database import get_db, close_connection, init_db, DATABASE # Import DATABASE constant

# --- Flask Application Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_and_random_key_for_blogging_platform' # IMPORTANT: Change this to a random, strong key

# Register database functions
app.teardown_appcontext(close_connection)

# --- Login Required Decorator ---
def login_required(view):
    """Decorator to ensure a user is logged in before accessing a route."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view

# --- Before Request: Load User ---
@app.before_request
def load_logged_in_user():
    """Loads the logged-in user from the session into Flask's global `g` object."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor()
        g.user = cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,)).fetchone()

# --- Routes ---

@app.route('/')
def index():
    """Renders the homepage displaying all blog posts."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            p.id, p.title, p.content, p.created_at, p.author_id, u.username as author_username
        FROM posts p JOIN users u ON p.author_id = u.id
        ORDER BY p.created_at DESC
    """)
    posts = cursor.fetchall()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=('GET', 'POST'))
def register():
    """Handles user registration."""
    if g.user:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        flash(error, 'error')
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    """Handles user login."""
    if g.user:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None
        user = cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('index'))

        flash(error, 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handles user logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/add', methods=('GET', 'POST'))
@login_required
def add_post():
    """Handles adding new blog posts (only for logged-in users)."""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        error = None

        if not title:
            error = 'Title is required.'
        elif not content:
            error = 'Content is required.'

        if error is None:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                (title, content, g.user['id'])
            )
            db.commit()
            flash('Post added successfully!', 'success')
            return redirect(url_for('index'))
        
        flash(error, 'error')
    return render_template('add_post.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """Renders a single blog post by its ID, including comments."""
    db = get_db()
    cursor = db.cursor()

    # Fetch post details
    post = cursor.execute("""
        SELECT
            p.id, p.title, p.content, p.created_at, p.author_id, u.username as author_username
        FROM posts p JOIN users u ON p.author_id = u.id
        WHERE p.id = ?
    """, (post_id,)).fetchone()

    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    
    # Render content as Markdown
    post_content_html = markdown.markdown(post['content'])

    # Fetch comments for the post
    comments = cursor.execute("""
        SELECT
            c.id, c.content, c.created_at, c.user_id, u.username as commenter_username
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at DESC
    """, (post_id,)).fetchall()

    return render_template('view_post.html', post=post, post_content_html=post_content_html, comments=comments)

@app.route('/post/<int:post_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_post(post_id):
    """Allows the author to edit their post."""
    db = get_db()
    cursor = db.cursor()
    post = cursor.execute("SELECT id, title, content, author_id FROM posts WHERE id = ?", (post_id,)).fetchone()

    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))

    if post['author_id'] != g.user['id']:
        flash('You are not authorized to edit this post.', 'error')
        return redirect(url_for('view_post', post_id=post_id))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        error = None

        if not title:
            error = 'Title is required.'
        elif not content:
            error = 'Content is required.'

        if error is None:
            cursor.execute(
                "UPDATE posts SET title = ?, content = ? WHERE id = ?",
                (title, content, post_id)
            )
            db.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('view_post', post_id=post_id))
        
        flash(error, 'error')

    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=('POST',))
@login_required
def delete_post(post_id):
    """Allows the author to delete their post."""
    db = get_db()
    cursor = db.cursor()
    post = cursor.execute("SELECT author_id FROM posts WHERE id = ?", (post_id,)).fetchone()

    if post is None:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))

    if post['author_id'] != g.user['id']:
        flash('You are not authorized to delete this post.', 'error')
        return redirect(url_for('view_post', post_id=post_id))

    cursor.execute("DELETE FROM comments WHERE post_id = ?", (post_id,)) # Delete comments first
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
    flash('Post and its comments deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/comment', methods=('POST',))
@login_required
def add_comment(post_id):
    """Allows logged-in users to add comments to a post."""
    content = request.form['comment_content']
    error = None

    if not content:
        error = 'Comment cannot be empty.'
    
    if error is None:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
            (post_id, g.user['id'], content)
        )
        db.commit()
        flash('Comment added!', 'success')
    else:
        flash(error, 'error')

    return redirect(url_for('view_post', post_id=post_id))


# --- Application Entry Point ---
if __name__ == '__main__':
    # Initialize the database ONLY if the database file does not exist
    if not os.path.exists(DATABASE):
        print(f"Database file '{DATABASE}' not found. Initializing database schema...")
        with app.app_context():
            init_db()
        print("Database initialized.")
    else:
        print(f"Database file '{DATABASE}' already exists. Skipping initialization.")

    # Run the Flask development server
    app.run(debug=True)
