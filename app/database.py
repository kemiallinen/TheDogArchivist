import sqlite3
import os
from flask import Flask

def get_database_path():
    app = Flask(__name__, instance_relative_config=True)
    return os.path.join(app.instance_path, 'dog_database.db')

DB_FILE = get_database_path()

def initialize_database():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE dogs (
            id INTEGER PRIMARY KEY,
            first_seen TEXT,
            last_seen TEXT,
            image_path TEXT
        )''')
        conn.commit()
        conn.close()

def add_or_update_dog(dog_id, image_path, first_seen, last_seen):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM dogs WHERE id = ?", (dog_id,))
    if c.fetchone() is None:
        c.execute("INSERT INTO dogs (id, first_seen, last_seen, image_path) VALUES (?, ?, ?, ?)",
                  (dog_id, first_seen, last_seen, image_path))
    else:
        c.execute("UPDATE dogs SET last_seen = ? WHERE id = ?", (last_seen, dog_id))
    conn.commit()
    conn.close()
