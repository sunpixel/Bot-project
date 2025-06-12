import sqlite3
from TG.src.config_manager import config

conn = sqlite3.connect(config.db_path)
cursor = conn.cursor()

cursor.execute('''

''')