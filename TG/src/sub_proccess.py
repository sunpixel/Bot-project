import os
import sqlite3
from telebot import types
from TG.src.modules.Processing.audio import receive_audio, check_audio
from TG.src.config_manager import config

def db_connection():
    return sqlite3.connect(config.db_path)

def clean_up():
    down_dir = os.path.join('TG', 'Data', 'Downloads')
    upld_dir = os.path.join('TG', 'Data', 'Uploads')
    downloads = os.listdir(down_dir)
    uploads = os.listdir(upld_dir)

    array = [[downloads, down_dir], [uploads, upld_dir]]

    for items in array:
        for item in items[0]:
            os.remove(os.path.join(items[1], item))

def start_func(msg, bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    get_create_user([msg.from_user.id, msg.from_user.username])

    btn_search = types.KeyboardButton('Search')
    btn_main = types.KeyboardButton('Main')
    btn_cart = types.KeyboardButton('Cart')
    markup.row(btn_search)
    markup.row(btn_main, btn_cart)
    markup.add()
    bot.send_message(msg.chat.id , 'Hi', reply_markup=markup)

def audio(msg, bot):
    data = receive_audio(msg, bot)
    v1 = check_audio(data[0], msg, bot, data[1])
    with open(v1, 'rb') as voice_file:
        try:
            bot.send_voice(msg.chat.id, voice_file)
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
            bot.send_message(
                msg.chat.id,
                "<b>An error has occurred while sending your voice message.</b>\n\n"
                "Please use the buttons below to get help with fixing common issues:",
                reply_markup=markup,
                parse_mode="HTML"
            )

def db_select_all_data(table):
    # Only to be used once per THREAD (function)
    conn = db_connection()
    cursor = conn.cursor()


    cursor.execute(f'''
    SELECT * FROM {table}
    ''')

    data = cursor.fetchall()
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

def is_admin(user_data):

    conn = db_connection()
    cursor = conn.cursor()

    user_id = int(user_data)

    cursor.execute('''
    SELECT * FROM admins WHERE user_id = ?
    ''', (user_id,))

    admin = cursor.fetchone()

    if admin:
        return True
    return False

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



