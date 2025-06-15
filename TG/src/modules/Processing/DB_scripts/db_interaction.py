from TG.src.config_manager import config
import sqlite3

def make_connection():
    return sqlite3.connect(config.db_path)


def on_add_to_cart(session, product_name):
    conn = make_connection()
    cursor = conn.cursor()

    user_id = session.user_id
    if ensure_cart_created(user_id, session):
        try:
            product_id = int(get_specific_product(product_name)[0])
        except Exception as e:
            print(f'Error: {e}')
            print('No such product exists')
            conn.close()
            # Stops code execution
            return

        try:
            cursor.execute('''
            SELECT * FROM CartItems
            WHERE product_id = ? AND cart_id = ?
            ''', (product_id, session.cart_id))
            item = cursor.fetchone()
            if item:
                quantity = int(item[3])
                quantity += 1
                cursor.execute('''
                UPDATE CartItems 
                SET quantity = ? 
                WHERE product_id = ? AND cart_id = ?
                ''', (quantity, product_id, session.cart_id))
            else:
                cursor.execute('''
                INSERT INTO CartItems (cart_id, product_id) VALUES (?, ?)
                ''', (session.cart_id, product_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print('here')
            print(f'Error: {e}')
            conn.rollback()
            conn.close()

def ensure_cart_created(user_id, session):
    conn = make_connection()
    cursor = conn.cursor()

    print(f'cart creation user id: {user_id}')

    try:
        cursor.execute('''
        SELECT id FROM Cart
        WHERE user_id = ?''', (user_id,))
        cart_exists = cursor.fetchone()
        if cart_exists:
            session.cart_id = cart_exists[0]
        else:
            cursor.execute('''
            INSERT INTO Cart (user_id)
            VALUES (?)
            ''', (user_id,))
            session.cart_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print('here')
        print(f'Error: {e}')
        conn.rollback()
        conn.close()
        return False


def get_specific_product(param):
    conn = make_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Products WHERE name = ?', (param,))

    product = cursor.fetchone()

    conn.close()
    return product

def cart_data_retrival(user_id):
    conn = make_connection()
    cursor = conn.cursor()
    cursor.execute('''
    select * from Cart where
    ''')

    cart_id = 0



    return cart_id