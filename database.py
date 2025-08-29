import sqlite3
from flask import g, current_app

DATABASE = 'blog_platform.db'

def get_db():
    """Establishes a database connection or returns an existing one."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Enable row factory to get dictionary-like rows
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    db = get_db()
    # Use current_app.open_resource as we're in a Flask application context
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
