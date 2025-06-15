import os
import sqlite3
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, Update
)
from telegram.constants import ParseMode
from TG.src.modules.Processing.audio import receive_audio, check_audio
from TG.src.config_manager import config
from TG.src.modules.Processing.DB_scripts.db_interaction import cart_data_retrival, ensure_cart_created

def db_connection():
    return sqlite3.connect(config.db_path)

class MainProcess:
    def __init__(self):
        pass

    @staticmethod
    def clean_up():
        down_dir = os.path.abspath(os.path.join(config.data_path, 'Downloads'))
        upld_dir = os.path.abspath(os.path.join(config.data_path, 'Uploads'))
        downloads = os.listdir(down_dir)
        uploads = os.listdir(upld_dir)

        array = [[downloads, down_dir], [uploads, upld_dir]]

        for items in array:
            for item in items[0]:
                os.remove(os.path.join(items[1], item))

    @staticmethod
    async def start_func(update: Update, context):
        markup = ReplyKeyboardMarkup(
            [
                [KeyboardButton('Search')],
                [KeyboardButton('Main'), KeyboardButton('Cart')]
            ],
            resize_keyboard=True
        )

        get_create_user([update.effective_user.id, update.effective_user.username])

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Hi',
            reply_markup=markup
        )
        return message.message_id

    @staticmethod
    async def audio(update: Update, context):
        MainProcess().clean_up()
        data = await receive_audio(update, context)
        v1 = await check_audio(data[0], update, context, data[1])
        with open(v1, 'rb') as voice_file:
            try:
                message = await context.bot.send_voice(update.effective_chat.id, voice_file)
            except Exception as e:
                await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("How to Allow Voice", url="https://core.telegram.org/bots/faq#voice-messages")],
                    [InlineKeyboardButton("Check Privacy Settings", url="https://telegram.org/faq#privacy")],
                    [InlineKeyboardButton("Contact Support", url="https://telegram.org/support")]
                ])
                print(e)
                message = await context.bot.send_message(
                    update.effective_chat.id,
                    "<b>An error has occurred while sending your voice message.</b>\n\n"
                    "Please use the buttons below to get help with fixing common issues:",
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML
                )
        return message.message_id

def db_select_all_data(table):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT * FROM {table}
    ''')
    data = cursor.fetchall()
    conn.close()
    print(data)

def get_create_user(user_data):
    conn = db_connection()
    cursor = conn.cursor()

    user_id = int(user_data[0])
    username = str(user_data[1])

    cursor.execute('''
    SELECT * FROM Users WHERE user_id = ?
    ''', (user_id,))

    user = cursor.fetchone()

    if not user:
        cursor.execute('''
        INSERT INTO Users (
        user_id,
        username
        ) VALUES (?, ?)
        ''', (user_id, username))
        conn.commit()
    conn.close()

def download_img():
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Go to URL', url='https://ya.ru')],
        [InlineKeyboardButton('Edit text', callback_data='edit'),
         InlineKeyboardButton('Delete photo', callback_data='delete')]
    ])
    return markup

class MainMenu:
    def __init__(self):
        pass

    @staticmethod
    def main_menu_data(limit=10, offset=0):
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM Products LIMIT ? OFFSET ?', (limit, offset)
        )
        data = cursor.fetchall()
        display_data = []
        for row in data:
            data = {'name': row[2], 'price': row[9]}
            display_data.append(data)
        conn.close()
        return display_data

    @staticmethod
    def main_menu_msg(data, data_set_atr):
        limit = data_set_atr[0]
        offset = data_set_atr[1]
        total = data_set_atr[2]

        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('🛒 Add to Cart 🛒', callback_data='add_to_cart'),
                InlineKeyboardButton('🔥 Buy Now 🔥', callback_data='buy_now')
            ],
            [InlineKeyboardButton('❓ More Info ❓', callback_data='more_info')]
        ])
        return markup

    @staticmethod
    def extra_menu_message(total, limit, offset):
        buttons = []
        if offset // 10 != 0:
            buttons.append(InlineKeyboardButton('⏪ Previous page', callback_data='previous_page'))
        if total - offset >= limit:
            buttons.append(InlineKeyboardButton('Next page ⏩', callback_data='next_page'))
        markup = InlineKeyboardMarkup([buttons] if buttons else [])
        return markup

    async def main_menu_handler(self, context, update, session, data_set_atr):
        limit = data_set_atr[0]
        offset = data_set_atr[1]
        total = data_set_atr[2]

        menu_data = MainMenu.main_menu_data(limit, offset)
        for data in menu_data:
            markup = self.main_menu_msg(data, [limit, offset, total])
            message = await context.bot.send_message(
                update.effective_chat.id,
                str(data['name']),
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
            session.add_text_data(message.text)
            session.add_message_id(message.message_id)
        markup = self.extra_menu_message(total, limit, offset)
        message = await context.bot.send_message(
            update.effective_chat.id,
            '-' * 20,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
        session.add_message_id(message.message_id)

def amount_in_table(table_name):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT count(*) FROM {table_name}
    ''')
    total = cursor.fetchone()[0]
    conn.close()
    if total:
        return total
    return 0

def get_cart_data(session):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('✅🛒 Buy 🛒✅', callback_data='buy_cart')],
        [InlineKeyboardButton('🗑️ Clear cart 🗑️', callback_data='do_clear_cart')],
        [InlineKeyboardButton('⏪ Back ⏪', callback_data='do_return')]
    ])
    if session.cart_id:
        data = cart_data_retrival(session.cart_id)
    else:
        ensure_cart_created(session.user_id, session)
        data = cart_data_retrival(session.cart_id)

    cart_message = "<b>🛍️ Your Shopping Cart 🛍️</b>\n<pre>\n"
    for item, qty, price in data:
        total = price * qty
        cart_message += f"{item:<25} │ ×{qty:<2} │ ₽  {total:>7.2f}\n"

    grand_total = sum(price * qty for _, qty, price in data)
    cart_message += f"\n{'GRAND TOTAL:':<25}         ₽   {grand_total:>7.2f}</pre>"