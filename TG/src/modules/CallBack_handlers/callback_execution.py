from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from TG.src.modules.Optional.admin_msg_handler import *
from TG.src.modules.Processing.DB_scripts.db_interaction import *
from TG.src.modules.Templates.db_data_templates import products_template

# All handler functions now use context instead of bot

async def handle_admin_add(callback, session, context):
    await session.clean_messages(callback.message.chat.id, context)
    msg = await context.bot.send_message(
        callback.message.chat.id,
        'Please provide user_id or username and command list, everything should be separated by whitespace'
    )
    session.add_message_id(msg.message_id)


async def handle_admin_add_input(message, session, context):
    parts = [p.strip() for p in message.text.split()]
    user_id = int(parts[0])
    commands = parts[1:]
    await context.bot.delete_message(message.chat.id, message.message_id)
    await session.clean_messages(message.chat.id, context)
    print(session.admin.admin_add([user_id, commands]))

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
    except Exception:
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
        except Exception:
            entry_name = message.text.strip()
            session.admin.delete_entry(entry_name, 'name')
    except Exception:
        pass

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
    string = str(msg.message.text)
    db_search = None
    if '\n' in string:
        for line in string.split('\n'):
            if line.startswith('name:'):
                db_search = line.split(':', 1)[1].strip()
                break
    else:
        db_search = string
    await on_add_to_cart(session, db_search)

async def handle_more_info(msg, session, context):
    msg_id = msg.message.message_id
    product = products_template.copy()
    db_search = session.text_data[session.message_ids.index(msg_id)]
    data = await get_specific_product(db_search)
    i = 1   # Made so that ID is not displayed
    for key in product.keys():
        product[key] = data[i]
        i += 1
    await session.clean_messages(msg.message.chat.id, context)
    text = ''
    for key, value in product.items():
        text += f"{key}: {value}\n"

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔥 Buy Now 🔥', callback_data='buy_now')],
        [InlineKeyboardButton('🛒 Add to Cart 🛒', callback_data='add_to_cart')],
        [InlineKeyboardButton('⏪ Back ⏪', callback_data='do_return')]
    ])
    message = await context.bot.send_message(
        msg.message.chat.id,
        text,
        reply_markup=markup
    )
    session.add_message_id(message.message_id)

async def handle_buy_cart(callback, session, context):
    # Implement your buy cart logic here
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

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('✅🛒 Buy 🛒✅', callback_data='buy_cart')],
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

async def handle_buy_now(callback, session, context):
    pass