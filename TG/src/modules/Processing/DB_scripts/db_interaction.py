from TG.src.config_manager import config
import sqlite3

def make_connection():
    return sqlite3.connect(config.db_path)


def on_add_to_cart(msg, session, product_name):
    conn = make_connection()
    cursor = conn.cursor()
    product_id = -1 # Made like this to throw an error
    user_id = int(msg.from_user.id)

    if ensure_cart_created(user_id, session):
        ''' Made to get ITEM_id if it exists '''
        try:
            product_id = int(get_specific_product(product_name)[0])
        except Exception as e:
            print(f'Error: {e}')
            print('No such product exists')

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
                conn.commit()
            else:
                cursor.execute('''
                Insert into CartItems (cart_id, product_id) VALUES (?, ?)
                ''')
            conn.close()
        except Exception as e:
            print(f'Error: {e}')
            conn.rollback()
            conn.close()

def ensure_cart_created(user_id, session):
    conn = make_connection()
    cursor = conn.cursor()

    cart_exists = False

    try:
        cursor.execute('''
        SELECT (user_id) FROM Cart
        WHERE user_id = ?''', (user_id,))
        cart_exists = cursor.fetchone()
        session.cart_id = cart_exists[0]
        return True if cart_exists else False

    except Exception as e:
        print(f'Error: {e}')


    if not cart_exists:
        try:
            cursor.execute('''
            INSERT INTO Cart (user_id)
            Values (?)
            ''', (user_id,))
            session.cart_id = cursor.fetchone()[0]
            return True
        except Exception as e:
            print(f'Error: {e}')
    return False


def get_specific_product(param):
    conn = make_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Products WHERE name = ?', (param,))

    product = cursor.fetchone()

    conn.close()
    return product