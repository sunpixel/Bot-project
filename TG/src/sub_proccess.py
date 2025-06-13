import os
import sqlite3
from telebot import types
from TG.src.modules.Processing.audio import receive_audio, check_audio
from TG.src.config_manager import config


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
    def start_func(msg, bot):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        get_create_user([msg.from_user.id, msg.from_user.username])

        btn_search = types.KeyboardButton('Search')
        btn_main = types.KeyboardButton('Main')
        btn_cart = types.KeyboardButton('Cart')
        markup.row(btn_search)
        markup.row(btn_main, btn_cart)
        markup.add()
        message = bot.send_message(msg.chat.id , 'Hi', reply_markup=markup)
        return message.message_id

    @staticmethod
    def audio(msg, bot):
        MainProcess().clean_up()
        data = receive_audio(msg, bot)
        v1 = check_audio(data[0], msg, bot, data[1])
        with open(v1, 'rb') as voice_file:
            try:
                message = bot.send_voice(msg.chat.id, voice_file)
            except Exception as e:
                bot.delete_message(msg.chat.id, msg.message_id)
                markup = types.InlineKeyboardMarkup()
                help_btn = types.InlineKeyboardButton("How to Allow Voice",
                                                      url="https://core.telegram.org/bots/faq#voice-messages")
                privacy_btn = types.InlineKeyboardButton("Check Privacy Settings", url="https://telegram.org/faq#privacy")
                contact_btn = types.InlineKeyboardButton("Contact Support", url="https://telegram.org/support")
                markup.row(help_btn)
                markup.row(privacy_btn)
                markup.row(contact_btn)
                print(e)
                message = bot.send_message(
                    msg.chat.id,
                    "<b>An error has occurred while sending your voice message.</b>\n\n"
                    "Please use the buttons below to get help with fixing common issues:",
                    reply_markup=markup,
                    parse_mode="HTML"
                )
        return message.message_id

def db_select_all_data(table):
    # Only to be used once per THREAD (function)
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

    cursor.execute(f'''
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
    markup = types.InlineKeyboardMarkup()
    move_to_btn = types.InlineKeyboardButton('Go to URL', 'https://ya.ru')

    # Callback_data means that a function will be called when this button is pressed

    edit_btn = types.InlineKeyboardButton('Edit text', callback_data='edit')
    delete_btn = types.InlineKeyboardButton('Delete photo', callback_data='delete')

    '''
        Each markup.row represents a different row
        To have several buttons in one row add them 
        as separate arguments into one line.
        They will be displayed in their order from
        left to right
    '''

    markup.row(move_to_btn)
    markup.row(edit_btn, delete_btn)
    markup.add()
    return markup

class MainMenu:
    def __init__(self):
        pass

    @staticmethod
    def main_menu_data(limit = 10, offset = 0):
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute(f'\n'
                       f'    select * from Products\n'
                       f'    limit {limit} offset {offset}\n'
                       f'    ')

        data = cursor.fetchall()

        display_data = []
        for row in data:
            data = {'name': row[1], 'price': row[2]}
            display_data.append(data)

        conn.close()
        return display_data

    @staticmethod
    def main_menu_msg(data, data_set_atr):
        limit = data_set_atr[0]
        offset = data_set_atr[1]
        total = data_set_atr[2]

        markup = types.InlineKeyboardMarkup()

        btn_add_to_cart = types.InlineKeyboardButton(
            text='🛒 Add to Cart 🛒',
            callback_data='add_to_cart'
        )

        btn_buy_now = types.InlineKeyboardButton(
            text='🔥 Buy Now 🔥',
            callback_data='buy_now'
        )

        btn_more_info = types.InlineKeyboardButton(
            text='❓ More Info ❓',
            callback_data='more_info'
        )

        markup.row(btn_add_to_cart, btn_buy_now)
        markup.row(btn_more_info)

        # Will be used ONCE as A Separate MSG SENT!!!

        if offset // 10 != 0:
            btn_previous_page = types.InlineKeyboardButton('⏪ Previous page', callback_data='previous_page')
        '''
            Will not be shown initially but will be shown
            on each other attempt
        '''
        if total - offset <= limit:
            btn_next_page = types.InlineKeyboardButton('Next page ⏩', callback_data='next_page')
        '''
            Should go like this:
            First will be 30 - 0 = 30 WORKS
            Second will be 30 - 10 = 20 WORKS
            Third will be 30 - 20 = 10 STOPS
        '''
        # markup.row(btn_previous_page, btn_next_page)

        markup.add()

        return markup

    @staticmethod
    def extra_menu_message(total, limit, offset):
        markup = types.InlineKeyboardMarkup()
        data = []
        print(total,limit,offset)
        if offset // 10 != 0:
            btn_previous_page = types.InlineKeyboardButton('⏪ Previous page', callback_data='previous_page')
            data.append(btn_previous_page)
        '''
            Will not be shown initially but will be shown
            on each other attempt
        '''
        if total - offset >= limit:
            btn_next_page = types.InlineKeyboardButton('Next page ⏩', callback_data='next_page')
            data.append(btn_next_page)
        '''
            Should go like this:
            First will be 30 - 0 = 30 WORKS
            Second will be 30 - 10 = 20 WORKS
            Third will be 30 - 20 = 10 STOPS
        '''
        if len(data) > 1:
            markup.row(data[0], data[1])
        else:
            markup.row(data[0])
        markup.add()
        return markup

        # markup.row(btn_previous_page, btn_next_page)
    def main_menu_handler(self, bot, msg, data_set_atr):
        limit = data_set_atr[0]
        offset = data_set_atr[1]
        total = data_set_atr[2]
        msg_ids = []
        text_data = []

        menu_data = MainMenu().main_menu_data(limit, offset)
        for data in menu_data:
            markup = self.main_menu_msg(data, [limit, offset, total])
            message = bot.send_message(msg.chat.id, str(data['name']), reply_markup=markup, parse_mode="HTML")
            text_data.append(message.text)
            msg_ids.append(int(message.message_id))
        markup = self.extra_menu_message(total, limit, offset)
        message = bot.send_message(msg.chat.id, '-' * 20, reply_markup=markup, parse_mode="HTML")
        text_data.append(message.text)
        msg_ids.append(int(message.message_id))
        return msg_ids, text_data

def amount_in_table(table_name):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(f'\n'
                   f'    select count(*) from {table_name}\n'
                   f'    ')
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_specific_data(param):
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Products WHERE name = ?', (param,))

    product = cursor.fetchone()

    conn.close()
    return product
