from TG.src.config_manager import config
import aiosqlite

async def make_connection():
    return await aiosqlite.connect(config.db_path)

async def on_add_to_cart(session, product_name):
    conn = await make_connection()
    cursor = await conn.cursor()

    user_id = session.user_id
    if await ensure_cart_created(user_id, session):
        try:
            product_id = int((await get_specific_product(product_name))[0])
        except Exception as e:
            print(f'Error: {e}')
            print('No such product exists')
            await conn.close()
            return

        try:
            await cursor.execute('''
            SELECT * FROM CartItems
            WHERE product_id = ? AND cart_id = ?
            ''', (product_id, session.cart_id))
            item = await cursor.fetchone()
            if item:
                quantity = int(item[3])
                quantity += 1
                await cursor.execute('''
                UPDATE CartItems 
                SET quantity = ? 
                WHERE product_id = ? AND cart_id = ?
                ''', (quantity, product_id, session.cart_id))
            else:
                await cursor.execute('''
                INSERT INTO CartItems (cart_id, product_id) VALUES (?, ?)
                ''', (session.cart_id, product_id))
            await conn.commit()
            await conn.close()
        except Exception as e:
            print('here')
            print(f'Error: {e}')
            await conn.rollback()
            await conn.close()
    await conn.close()

async def ensure_cart_created(user_id, session):
    conn = await make_connection()
    cursor = await conn.cursor()

    print(f'cart creation user id: {user_id}')

    try:
        await cursor.execute('''
        SELECT id FROM Cart
        WHERE user_id = ?''', (user_id,))
        cart_exists = await cursor.fetchone()
        if cart_exists:
            session.cart_id = cart_exists[0]
        else:
            await cursor.execute('''
            INSERT INTO Cart (user_id)
            VALUES (?)
            ''', (user_id,))
            session.cart_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return True

    except Exception as e:
        print('here')
        print(f'Error: {e}')
        await conn.rollback()
        await conn.close()
        return False

async def get_specific_product(param):
    conn = await make_connection()
    cursor = await conn.cursor()

    await cursor.execute('SELECT * FROM Products WHERE name = ?', (param,))

    product = await cursor.fetchone()

    await conn.close()
    return product

async def cart_data_retrival(cart_id):
    conn = await make_connection()
    cursor = await conn.cursor()

    to_return = []

    await cursor.execute('''
        SELECT * FROM CartItems 
        WHERE cart_id = ?
    ''', (cart_id,))
    data = await cursor.fetchall()
    result =  [t[-2:] for t in data]

    for a in result:
        await cursor.execute('''
            SELECT name, price FROM Products
            WHERE id = ?
        ''', (a[0],))
        data = await cursor.fetchone()
        name = data[0]
        price = data[1]
        to_return.append([name, a[1], (price * int(a[1])) ])
    await conn.close()
    print(f'Cart {cart_id} contains: \n {to_return}')
    return to_return

async def convert_from_bytes(blob_data, full_file_path):
    with open(full_file_path, 'wb') as file:
        img = file.write(blob_data)
        print(f'Data saved to: {full_file_path}')




