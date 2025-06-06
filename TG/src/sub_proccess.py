import os
from telebot import types

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

    btn_search = types.KeyboardButton('Search')
    btn_main = types.KeyboardButton('Main')
    btn_cart = types.KeyboardButton('Cart')
    markup.row(btn_search)
    markup.row(btn_main, btn_cart)
    markup.add()
    bot.send_message(msg.chat.id , 'Hi!!', reply_markup=markup)