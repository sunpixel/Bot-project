import os
from telebot import types

def clean_up():
    directory = os.path.join('TG', 'Data', 'Downloads')
    items = os.listdir(directory)
    for item in items:
        os.remove(os.path.join(directory, item))

def start_func(msg, bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_search = types.KeyboardButton('Search')
    btn_main = types.KeyboardButton('Main')
    btn_cart = types.KeyboardButton('Cart')
    markup.row(btn_search)
    markup.row(btn_main, btn_cart)
    markup.add()
    bot.send_message(msg.chat.id , 'Hi!!', reply_markup=markup)