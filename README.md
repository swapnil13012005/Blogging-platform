# Simple Blogging Platform with Flask

This is a lightweight, feature-rich blogging platform built using Flask. It allows users to register, log in, create, edit, and delete blog posts, as well as comment on posts. Blog content supports Markdown for rich text formatting.

## ✨ Features

- **User Authentication:** Secure registration, login, and logout. Passwords are hashed.
- **Create Posts:** Authenticated users can write and publish new blog posts.
- **Edit & Delete Posts:** Post authors can edit or delete their own posts.
- **Markdown Support:** Blog post content is rendered with Markdown.
- **Commenting System:** Logged-in users can leave comments on any blog post.
- **Responsive Design:** Styled with Tailwind CSS.
- **SQLite Database:** Stores users, posts, and comments.

## 💻 Technologies Used

- Python 3.x
- Flask
- SQLite3
- Werkzeug (for password hashing)
- Python-Markdown
- Jinja2 (Flask's templating engine)
- Tailwind CSS

## 🚀 Setup Instructions

1. **Clone the Repository (or create the files):**

    ```
    blogging_platform/
    ├── app.py
    ├── database.py
    ├── schema.sql
    └── templates/
        ├── base.html
        ├── index.html
        ├── add_post.html
        ├── view_post.html
        ├── register.html
        ├── login.html
        └── edit_post.html
    ```

2. **Create a Virtual Environment (Recommended):**

    ```sh
    python -m venv venv
    ```

3. **Activate the Virtual Environment:**

    - Windows: `.\venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`

4. **Install Dependencies:**

    ```sh
    pip install Flask Werkzeug Markdown
    ```

5. **Initialize the Database:**

    The database (`blog_platform.db`) will be automatically created and initialized when you run `app.py` for the first time.  
    To reset, delete the `blog_platform.db` file before running the application.

6. **Run the Application:**

    ```sh
    python app.py
    ```

    The server will run at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## 🌐 Usage

- **Register:** Create a new user account.
- **Log In:** Access your account.
- **Create Posts:** Write and publish blog entries (Markdown supported).
- **View Posts:** Click on any post title to view its content and comments.
- **Edit/Delete Posts:** Authors can edit or delete their own posts.
- **Add Comments:** Logged-in users can comment on any post.
- **Log Out:** End your session.

## 🗃️ Database

- **users:** Stores user authentication details.
- **posts:** Stores blog post information.
- **comments:** Stores comments on posts.

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for improvements or new features!