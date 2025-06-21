from telegram.constants import ParseMode
from telegram import WebAppInfo
from TG.src.modules.Optional.admin_msg_handler import *
from TG.src.modules.Processing.DB_scripts.db_interaction import *
from TG.src.modules.Templates.db_data_templates import products_template
from TG.src.sub_proccess import send_image_blob


# All handler functions now use context instead of bot

async def handle_admin_add(callback, session, context):
    await session.clean_messages(callback.message.chat.id, context)
    msg = await context.bot.send_message(
        callback.message.chat.id,
        'Please provide user_id or username and command list, everything should be separated by whitespace'
    )
    session.add_message_id(msg.message_id)
    session.next_handler = 'admin_add_input'
    session.step = 0
    session.collected_data = []


async def handle_admin_add_input(message, session, context):
    parts = [p.strip() for p in message.text.split()]
    user_id = int(parts[0])
    commands = parts[1:]
    # Deletes user input
    await context.bot.delete_message(message.chat.id, message.message_id)
    # Clears bot msgs
    await session.clean_messages(message.chat.id, context)
    await session.admin.admin_add([user_id, commands])

async def handle_admin_delete(callback, session, context):
    await session.clean_messages(callback.message.chat.id, context)
    msg = await context.bot.send_message(
        callback.message.chat.id,
        'Enter admin user_id to delete'
    )
    session.add_message_id(msg.message_id)
    # You need to implement a mechanism for the next step (e.g., ConversationHandler)

async def handle_admin_delete_input(message, session, context):
    try:
        await context.bot.delete_message(message.chat.id, message.message_id)
        await session.clean_messages(message.chat.id, context)
        user_id = int(message.text)
        session.admin.admin_delete(user_id)
    except TypeError:
        pass

async def handle_entry_new(callback, session, context):
    await session.clean_messages(callback.message.chat.id, context)
    msg = await context.bot.send_message(
        callback.message.chat.id,
        'Try to add an entry'
    )
    session.add_message_id(msg.message_id)

async def handle_entry_delete(callback, session, context):
    await session.clean_messages(callback.message.chat.id, context)
    await context.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    msg = await context.bot.send_message(
        callback.message.chat.id,
        'To delete an entry provide name or id'
    )
    session.add_message_id(msg.message_id)

async def handle_entry_delete_input(message, session, context):
    try:
        await context.bot.delete_message(message.chat.id, message.message_id)
        await session.clean_messages(message.chat.id, context)
        try:
            entry_id = int(message.text)
            session.admin.delete_entry(entry_id, 'id')
        except TypeError:
            entry_name = message.text.strip()
            session.admin.delete_entry(entry_name, 'name')
    except Exception as e:
        print(f'Unhandled error: {e}')

async def handle_entry_modify(callback, session, context):
    await session.clean_messages(callback.message.chat.id, context)
    msg = await context.bot.send_message(
        callback.message.chat.id,
        'Try to modify an entry'
    )
    session.add_message_id(msg.message_id)

async def handle_edit(callback, session, context):
    await session.clean_messages(callback.message.chat.id, context)
    if session.text_data:
        new_text = f"Edited: {session.text_data[0]}"  # Using first item as example
        await context.bot.edit_message_text(
            new_text,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )

async def handle_delete(callback, session, context):
    await context.bot.delete_message(callback.message.chat.id, callback.message.message_id)

async def handle_add_to_cart(msg, session, context):
    db_search = msg.message.caption.split('\n', 1)[0]
    await on_add_to_cart(session, db_search)

async def handle_more_info(msg, session, context):
    msg_id = msg.message.message_id
    product = products_template.copy()
    db_search = msg.message.caption.split('\n', 1)[0]
    data = await get_specific_product(db_search)
    image_stream = None

    i = 1   # Made so that ID is not displayed
    for key in product.keys():
        if key == 'image':
            image_stream = await send_image_blob(db_search)
        else:
            # Sets values
            product[key] = data[i]
        i += 1
    await session.clean_messages(msg.message.chat.id, context)
    text = ''
    for key, value in product.items():
        if key == 'image':
            pass
        else:
            text += (f"{key}: {value}\n"
                     f"{'-'* 10}\n")

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔥 Buy Now 🔥', callback_data='buy_now')],
        [InlineKeyboardButton('🛒 Add to Cart 🛒', callback_data='add_to_cart')],
        [InlineKeyboardButton('⏪ Back ⏪', callback_data='do_return')]
    ])
    message = await context.bot.send_photo(
        msg.message.chat.id,
        photo=image_stream,
        caption=text,
        reply_markup=markup
    )
    session.add_message_id(message.message_id)


async def handle_buy_cart(callback, session, context):
    pass

async def handle_do_clear_cart(callback, session, context):
    conn = await make_connection()
    cursor = await conn.cursor()
    await cursor.execute('''
        DELETE from CartItems
        WHERE quantity > 0 AND cart_id = ?
    ''', (session.cart_id,))
    await conn.commit()
    await conn.close()

    """
    HERE YOU NEED TO SET UP YOUR WEBAPP URL
    This URL should point to your web application that handles the cart.
    SO ROOT URL SHOULD BE YOUR NGROK URL and USER_ID SHOULD BE YOUR USER ID
    For example, if your ngrok URL is https://example.ngrok.io and your user_id is 123456,
    the webapp_url would be:
    https://example.ngrok.io/123456
    """
    webapp_url =  config.webapp_url + str(session.user_id)

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('✅🛒 Buy 🛒✅', web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton('🗑️ Clear cart 🗑️', callback_data='do_clear_cart')],
        [InlineKeyboardButton('⏪ Back ⏪', callback_data='do_return')]
    ])

    cart_message = "<b>🛍️ Your Shopping Cart 🛍️</b>\n<pre>\n"
    cart_message += f"\n{'GRAND TOTAL:':<25}         ₽   0</pre>"

    await context.bot.edit_message_text(
        text=cart_message,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )

async def get_all_users(is_admin: bool):
    conn = await make_connection()
    cursor = await conn.cursor()

    # Retrieve all admins
    if is_admin:
        sql = f'SELECT * from Users where user_id in (select user_id from admins)'
    # Retrieve all NOT admins
    else:
        sql = f'SELECT * from Users where user_id not in (select user_id from admins)'

    await cursor.execute(sql)
    data = await cursor.fetchall()

async def handle_buy_now(callback, session, context):
    pass