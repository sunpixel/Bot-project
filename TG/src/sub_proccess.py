import os
import sqlite3
from telebot import types
from TG.src.modules.Processing.audio import receive_audio, check_audio

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.abspath(os.path.join(script_dir, '..', 'Data', 'DataBase', 'shop.db'))

def db_connection():
    return sqlite3.connect(db_path)

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

    get_create_user([msg.from_user.id, msg.chat.id])

    btn_search = types.KeyboardButton('Search')
    btn_main = types.KeyboardButton('Main')
    btn_cart = types.KeyboardButton('Cart')
    markup.row(btn_search)
    markup.row(btn_main, btn_cart)
    markup.add()
    bot.send_message(msg.chat.id , '', reply_markup=markup)

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

    cursor.execute(f'''
    SELECT * FROM Users WHERE TG_User_ID = ?
    ''', (user_data[0]))

    user = cursor.fetchone()

    if not user:
        cursor.execute('''
        INSERT INTO Users (
        TG_User_ID,
        TG_Chat_ID
        ) VALUES (?, ?)
        ''', (user_data[0], user_data[1]))
        connection.commit()
