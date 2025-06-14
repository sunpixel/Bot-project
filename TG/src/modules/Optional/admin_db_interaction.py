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

def add_new_entry(entry_table, entry_data, user_id):
    conn = make_connection()
    cursor = conn.cursor()

    admin = check_existence('admins', 'user_id', user_id)

    if not admin or not check_command(admin[2], 'new_entry'):
        conn.close()
        return f'Permission denied for user {user_id}'

    try:
        columns = ', '.join(entry_data.keys())
        values = ', '.join(['?'] * len(entry_data))
        cursor.execute(f'''
        INSERT INTO {entry_table} ({columns})
        VALUES ({values})
        ''', tuple(entry_data.values()))
        return f'Data successfully added to {entry_table}'

    except Exception as e:
        print(f'Error: {e}')
        return 'Error occurred'

    finally:
        conn.close()

def delete_entry(entry_data, entry_column):
    conn = make_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f'''
        SELECT * FROM Products WHERE {entry_column} = ?
        ''', (entry_data,))
        product = cursor.fetchone()
        if product:
            cursor.execute(f'''
            DELETE FROM Products WHERE {entry_column} = ?''')
            print(f'Data successfully deleted from Products')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'Error: {e}')
        conn.rollback()
        conn.close()


def modify_entry(entry_data, entry_value, entry_column):
    conn = make_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f'''
        UPDATE Products 
        SET {entry_column}
        WHERE {entry_column} = ?
        ''', (entry_value, entry_column))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f'Error entry modification: {e}')
        conn.rollback()
        conn.close()
