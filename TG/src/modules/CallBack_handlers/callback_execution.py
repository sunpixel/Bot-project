from TG.src.modules.Optional.admin_msg_handler import *
from TG.src.modules.Processing.DB_scripts.db_interaction import *
from TG.src.modules.Templates.db_data_templates import products_template


def handle_admin_add(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id, 'Please provide user_id or username and command list,'
                                                     'everything should be separated by whitespace')
    session.add_message_id(msg.message_id)
    bot.register_next_step_handler(msg, handle_admin_add_input, session, bot)

def handle_admin_add_input(message, session, bot):
    parts = [p.strip() for p in message.text.split()]
    user_id = int(parts[0])
    commands = parts[1:]
    bot.delete_message(message.chat.id, message.id)
    session.clean_messages(message.chat.id)
    print(session.admin.admin_add([user_id, commands]))


def handle_admin_delete(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Enter admin user_id to delete')
    session.add_message_id(msg.message_id)
    bot.register_next_step_handler(msg, handle_admin_delete_input, session, bot)

def handle_admin_delete_input(message, session, bot):
    try:
        bot.delete_message(message.chat.id, message.id)
        session.clean_messages(message.chat.id)
        user_id = int(message.text)
        session.admin.admin_delete(user_id)
    except:
        pass


def handle_entry_new(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Try to add an entry')
    session.add_message_id(msg.message_id)


def handle_entry_delete(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    bot.delete_message(callback.message.chat.id, callback.message.id)
    msg = bot.send_message(callback.message.chat.id,
                           'To delete an entry provide'
                           'name or id')
    session.add_message_id(msg.message_id)


def handle_entry_delete_input(message, session, bot):
    try:
        bot.delete_message(message.chat.id, message.id)
        session.clean_messages(message.chat.id)
        try:
            entry_id = int(message.text)
            session.admin.delete_entry(entry_id, 'id')
        except:
            entry_name = message.text.strip()
            session.admin.delete_entry(entry_name, 'name')
    except:
        pass

def handle_entry_modify(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    admin = AdminMessageHandler()
    msg = bot.send_message(callback.message.chat.id,
                           'Try to modify an entry')
    session.add_message_id(msg.message_id)
    admin = None

def handle_edit(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    if session.text_data:
        new_text = f"Edited: {session.text_data[0]}"  # Using first item as example
        bot.edit_message_text(new_text, callback.message.chat.id, callback.message.message_id)


def handle_delete(callback, session, bot):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)

def handle_add_to_cart(msg, session, bot):
    string = str(msg.message.text)
    db_search = None
    if string.find('\n') != -1:
        for line in string.split('\n'):
            if line.startswith('name:'):
                db_search = line.split(':', 1)[1].strip()
                break
    else:
        db_search = string
    on_add_to_cart(session, db_search)


def handle_more_info(msg, session, bot):
    markup = types.InlineKeyboardMarkup(row_width=1)
    msg_id = msg.message.message_id
    product = products_template.copy()
    db_search = session.text_data[session.message_ids.index(msg_id)]
    data = get_specific_product(db_search)
    i = 1   # Made so that ID is not displayed
    for key in product.keys():
        product[key] = data[i]
        i += 1
    session.clean_messages(msg.message.chat.id)
    text = ''
    for key, value in product.items():
        text += f"{key}: {value}\n"

    btn_add_to_cart = types.InlineKeyboardButton(
        text='🛒 Add to Cart 🛒',
        callback_data='add_to_cart'
    )

    btn_buy_now = types.InlineKeyboardButton(
        text='🔥 Buy Now 🔥',
        callback_data='buy_now'
    )

    btn_do_return = types.InlineKeyboardButton(
        text='⏪ Back ⏪',
        callback_data='do_return'
    )

    markup.add(btn_buy_now, btn_add_to_cart, btn_do_return)
    message = bot.send_message(msg.message.chat.id, text,
                               reply_markup=markup)
    session.add_message_id(message.message_id)

def handle_buy_cart(callback, session, bot):
    pass

def handle_do_clear_cart(callback, session, bot):
    conn = make_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE from CartItems
        WHERE quantity > 0 AND cart_id = ?
    ''', (session.cart_id,))
    conn.commit()
    conn.close()

    cart_message = "<b>🛍️ Your Shopping Cart 🛍️</b>\n<pre>\n"
    cart_message += f"\n{'GRAND TOTAL:':<25}         ₽   0</pre>"

    bot.edit_message_text(text=cart_message,
                          chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          parse_mode='HTML')

