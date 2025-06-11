import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.abspath(os.path.join(script_dir, '..', '..', 'Data', 'DataBase', 'shop.db'))
print(db_path)

connection = sqlite3.Connection(db_path)
cursor = connection.cursor()

# Create all tables in a DB and make connections

cursor.executescript('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    cart_id INTEGER
);

CREATE TABLE IF NOT EXISTS Cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users (id)
);

CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS Products_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    details TEXT,
    capacity INTEGER,
    min_temp NUMERIC,
    max_temp NUMERIC,
    type TEXT,
    FOREIGN KEY (product_id) REFERENCES Products (id)
);

CREATE TABLE IF NOT EXISTS admins (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
commands TEXT
)
''')

connection.commit()
connection.close()