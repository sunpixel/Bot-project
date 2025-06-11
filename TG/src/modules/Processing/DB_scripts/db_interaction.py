from TG.src.config_manager import config
import sqlite3

def get_all_products(filter=None):
    conn = sqlite3.connect(config.db_path)
    cursor = conn.cursor()

    cursor.execute('''
    
    ''')