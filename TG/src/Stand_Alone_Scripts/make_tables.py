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
    username TEXT
);

CREATE TABLE IF NOT EXISTS Cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image BLOB,
    name TEXT NOT NULL,
    details TEXT,
    speed REAL,
    capacity INTEGER,
    min_temp NUMERIC,
    max_temp NUMERIC,
    type TEXT,
    price REAL NOT NULL,
    embedding BLOB
);

CREATE TABLE IF NOT EXISTS CartItems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER,
    product_id INTEGER,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (cart_id) REFERENCES Cart (id),
    FOREIGN KEY (product_id) REFERENCES Products (id)
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    commands TEXT
);
''')

connection.commit()
connection.close()
