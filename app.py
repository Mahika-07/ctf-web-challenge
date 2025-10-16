import sqlite3
import os
from flask import Flask, render_template, request, redirect, make_response, g

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, 'ctf.db')

app = Flask(__name__, template_folder='templates')




# --- Database Setup ---
def get_db():
    """
    Return a sqlite3 connection stored on flask.g for the request lifetime.
    Uses check_same_thread=False so the dev server won't error on threaded access.
    (OK for testing/CTF; use a proper DB in production.)
    """
    db = getattr(g, "_database", None)
    if db is None:
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
            # swallow errors during teardown so they don't break response streaming
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
    message = "No results found." # Default message

    if request.method == 'POST':
        user_input = request.form.get('filename', '')
        # INTENTIONAL VULNERABILITY for CTF
        query = f"SELECT name, content FROM files WHERE name = '{user_input}'"
        try:
            cur = get_db().cursor()
            # This is insecure on purpose for the challenge
            cur.execute(query)
            rows = cur.fetchall()
            # The logic requires the injection to return MORE than one row
            if len(rows) > 1:
                results = rows
                message = None # Clear message if we have results
        except Exception:
            # Suppress errors for realism
            results = []

    return render_template('storage.html',
                           results=results,
                           query=query,
                           user_input=user_input,
                           message=message)

if __name__ == '__main__':
    # Make sure you have run db_init.py once to create the database
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run 'python db_init.py' first.")
    else:
        app.run(debug=True, host='127.0.0.1', port=5000)