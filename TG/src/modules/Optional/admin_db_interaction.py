import sqlite3
from TG.src.config_manager import config

def make_connection():
    return sqlite3.connect(config.db_path)

def check_existence(table, parameter, value: int):
    conn = make_connection()
    cursor = conn.cursor()

    cursor.execute(f'''
    SELECT * FROM {table} WHERE {parameter} = ?
    ''', (value,))

    data = cursor.fetchone()
    conn.close()

    return data

def check_command(user, command):
    '''
    :param user: (from DB)
    :param command: (comes as string)
    :return:
    '''
    commands = str(user[2]).split(',')
    for i in commands:
        if i == command:
            return True
    return False


def data_exists(table_name, column_value_pairs):
    """Check if a record exists based on column-value pairs."""
    conn = make_connection()
    cursor = conn.cursor()
    try:
        where_clause = " AND ".join([f"{col} = ?" for col in column_value_pairs.keys()])
        query = f"SELECT 1 FROM {table_name} WHERE {where_clause}"
        cursor.execute(query, tuple(column_value_pairs.values()))
        if cursor.fetchone():
            return True
        else: return False
    finally:
        conn.close()

def add_new_admin(user_data):
    conn = make_connection()
    cursor = conn.cursor()

    # Function that will perform conversion from array to a string
    commands = lambda arr: ",".join(arr)

    # Allows for easy setup of all the commands available to admin

    user_id = int(user_data[0])
    allowed_commands = commands(user_data[1])



    try:
        cursor.execute('''
        INSERT INTO admins (user_id, commands)
        VALUES (?, ?)
        ''', (user_id, allowed_commands))
        conn.commit()
        return (f'User {user_id} added to admins with'
                f'{allowed_commands}')
    except Exception as e:
        print(f'Error: {e}')
        return f'User {user_id} already exists'
    finally:
        conn.close()

def delete_admin(user_data):
    conn = make_connection()
    cursor = conn.cursor()
    user_id = int(user_data)

    try:
        cursor.execute('''
        DELETE FROM admins WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        return f'User {user_id} successfully deleted from admins'
    except Exception as e:
        conn.rollback()
        print(f'Error: {e}')
        return f'An error has occurred.'
    finally:
        conn.close()


'''
    Some of the entries are performed automatically
    on USER interaction
    on USER ADD_TO_CART
    on USER BUTTON_ACTION
'''

def add_new_entry(entry_table, entry_data):
    conn = make_connection()
    cursor = conn.cursor()
    try:
        columns = ', '.join(entry_data.keys())
        placeholders = ', '.join(['?'] * len(entry_data))
        sql = f'INSERT INTO {entry_table} ({columns}) VALUES ({placeholders})'
        cursor.execute(sql, tuple(entry_data.values()))
        conn.commit()
        result = f'Data successfully added to {entry_table}'
    except Exception as e:
        print(f'Error: {e}')
        conn.rollback()
        result = 'Error occurred'
    conn.close()
    return result

def update_entry(entry_table, entry_data, where_clause, where_args):
    """
    entry_table: str, table name
    entry_data: dict, columns and their new values
    where_clause: str, e.g. "id = ?"
    where_args: tuple/list, values for the WHERE clause
    """
    conn = make_connection()
    cursor = conn.cursor()
    try:
        set_clause = ', '.join([f"{col}=?" for col in entry_data.keys()])
        sql = f'UPDATE {entry_table} SET {set_clause} WHERE {where_clause}'
        cursor.execute(sql, tuple(entry_data.values()) + tuple(where_args))
        conn.commit()
        result = f'Data successfully updated in {entry_table}'
    except Exception as e:
        print(f'Error: {e}')
        conn.rollback()
        result = 'Error occurred'
    conn.close()
    return result

def delete_entry(entry_table, column_name, value):
    """
    entry_table: str, table name
    column_name: str, column to match in WHERE clause
    value: value to match for deletion
    """
    conn = make_connection()
    cursor = conn.cursor()
    try:
        sql = f'DELETE FROM {entry_table} WHERE {column_name} = ?'
        cursor.execute(sql, (value,))
        conn.commit()
        result = f'Data successfully deleted from {entry_table}'
    except Exception as e:
        print(f'Error: {e}')
        conn.rollback()
        result = 'Error occurred'
