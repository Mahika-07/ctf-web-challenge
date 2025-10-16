import sqlite3
import os
from flask import Flask, render_template, request, redirect, make_response, g

# Use the /tmp directory, which is writable on Vercel
DB_PATH = os.path.join('/tmp', 'ctf.db')

def init_db():
    """Creates and populates the database if it doesn't exist."""
    # This check now looks inside /tmp
    if not os.path.exists(DB_PATH):
        print("Database not found in /tmp. Creating and seeding it now...")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS files (name TEXT PRIMARY KEY, content TEXT)')
        files = [
            ('readme.txt', 'This is just a readme.'),
            ('notes.txt', 'Some ordinary notes.'),
            ('flag.txt', 'l8xieee{sql_c00kies_wEb}'),
            ('secret.txt', 'You found a secret file but not the flag.')
        ]
        c.executemany('INSERT OR REPLACE INTO files (name, content) VALUES (?, ?)', files)
        conn.commit()
        conn.close()
        print("Database initialized (ctf.db).")

app = Flask(__name__)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        init_db()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        g._database = conn
    return g._database

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

@app.route('/robots.txt')
def robots():
    txt = "User-agent: *\nDisallow: /feedback\n"
    return make_response(txt, 200, {'Content-Type': 'text/plain'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feedback')
def hidden():
    reveal = request.cookies.get('reveal', 'false').lower()
    show_sql_link = (reveal == 'true')
    return render_template('feedback.html', show_sql_link=show_sql_link)

@app.route('/storage', methods=['GET', 'POST'])
def storage_page():
    results = []
    query = None
    user_input = ''
    message = "No results found."

    if request.method == 'POST':
        user_input = request.form.get('filename', '')
        query = f"SELECT name, content FROM files WHERE name = '{user_input}'"
        try:
            cur = get_db().cursor()
            cur.execute(query)
            rows = cur.fetchall()
            if len(rows) > 1:
                results = rows
                message = None
        except Exception as e:
            # For debugging, you can print the error to the Vercel logs
            print(f"An error occurred: {e}")
            results = []

    return render_template('storage.html',
                           results=results,
                           query=query,
                           user_input=user_input,
                           message=message)