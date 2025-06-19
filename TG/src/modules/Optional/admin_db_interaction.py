import aiosqlite
from TG.src.config_manager import config

async def make_connection():
    return aiosqlite.connect(config.db_path)

async def check_existence(table, parameter, value: int):
    conn = await make_connection()
    cursor = await conn.cursor()

    await cursor.execute(f'''
    SELECT * FROM {table} WHERE {parameter} = ?
    ''', (value,))

    data = await cursor.fetchone()
    await conn.close()

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


async def data_exists(table_name, column_value_pairs):
    """Check if a record exists based on column-value pairs."""
    conn = await make_connection()
    cursor = await conn.cursor()
    try:
        where_clause = " AND ".join([f"{col} = ?" for col in column_value_pairs.keys()])
        query = f"SELECT 1 FROM {table_name} WHERE {where_clause}"
        await cursor.execute(query, tuple(column_value_pairs.values()))
        if await cursor.fetchone():
            await conn.close()
            return True
        else:
            await conn.close()
            return False
    except Exception as e:
        await conn.close()
        print(f'Error: {e}')

async def add_new_admin(user_data):
    conn = await make_connection()
    cursor = await conn.cursor()

    # Function that will perform conversion from array to a string
    commands = lambda arr: ",".join(arr)

    # Allows for easy setup of all the commands available to admin

    user_id = int(user_data[0])
    allowed_commands = commands(user_data[1])

    try:
        await cursor.execute('''
        INSERT INTO admins (user_id, commands)
        VALUES (?, ?)
        ''', (user_id, allowed_commands))
        await conn.commit()
        return (f'User {user_id} added to admins with'
                f'{allowed_commands}')
    except Exception as e:
        print(f'Error: {e}')
        return f'User {user_id} already exists'
    finally:
        await conn.close()

async def delete_admin(user_data):
    conn = await make_connection()
    cursor = await conn.cursor()
    try:
        user_id = int(user_data)
    except TypeError:
        print('User_id is not an int')

    try:
        await cursor.execute('''
        DELETE FROM admins WHERE user_id = ?
        ''', (user_id,))
        await conn.commit()
        return f'User {user_id} successfully deleted from admins'
    except Exception as e:
        await conn.rollback()
        print(f'Error: {e}')
        return f'An error has occurred.'
    finally:
        await conn.close()

async def add_new_entry(entry_table, entry_data):
    conn = await make_connection()
    cursor = await conn.cursor()
    try:
        columns = ', '.join(entry_data.keys())
        placeholders = ', '.join(['?'] * len(entry_data))
        sql = f'INSERT INTO {entry_table} ({columns}) VALUES ({placeholders})'
        await cursor.execute(sql, tuple(entry_data.values()))
        await conn.commit()
        result = f'Data successfully added to {entry_table}'
    except Exception as e:
        print(f'Error: {e}')
        await conn.rollback()
        result = 'Error occurred'
    await conn.close()
    return result

async def update_entry(entry_table, entry_data, where_clause, where_args):
    """
    entry_table: str, table name
    entry_data: dict, columns and their new values
    where_clause: str, e.g. "id = ?"
    where_args: tuple/list, values for the WHERE clause
    """
    conn = await make_connection()
    cursor = await conn.cursor()
    try:
        set_clause = ', '.join([f"{col}=?" for col in entry_data.keys()])
        sql = f'UPDATE {entry_table} SET {set_clause} WHERE {where_clause}'
        await cursor.execute(sql, tuple(entry_data.values()) + tuple(where_args))
        await conn.commit()
        result = f'Data successfully updated in {entry_table}'
    except Exception as e:
        print(f'Error: {e}')
        await conn.rollback()
        result = 'Error occurred'
    await conn.close()
    return result

async def delete_entry(entry_table, column_name, value):
    """
    entry_table: str, table name
    column_name: str, column to match in WHERE clause
    value: value to match for deletion
    """
    conn = await make_connection()
    cursor = await conn.cursor()
    try:
        sql = f'DELETE FROM {entry_table} WHERE {column_name} = ?'
        await cursor.execute(sql, (value,))
        await conn.commit()
    except Exception as e:
        print(f'Error: {e}')
        await conn.rollback()


async def convert_to_bytes(full_file_path):
    with open(full_file_path, 'rb') as file:
        data = file.read()
        return data