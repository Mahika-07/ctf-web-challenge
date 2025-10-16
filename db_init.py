# db_init.py
import sqlite3

conn = sqlite3.connect('ctf.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS files (name TEXT PRIMARY KEY, content TEXT)')
# seed some "files"
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
