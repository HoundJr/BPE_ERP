import sqlite3
import os

DB_PATH = 'instance/erp.sqlite3'
os.makedirs('instance', exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    due_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    date_created TEXT NOT NULL,
    hourly_rate REAL,
    estimated_hours REAL,
    material_cost REAL,
    markup_percent REAL,
    total_price REAL,
    pdf_path TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
''')

conn.commit()
conn.close()
print("Database initialized.")
