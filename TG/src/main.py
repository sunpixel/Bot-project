import os
from telebot import types
from sub_proccess import *
from TG.src.config_manager import config
import telebot

bot = telebot.TeleBot(config.get_api_key('telegram'))

'''Global variable for ease of use'''

total = 0
offset = 0
limit = 10

'''Only this fue universally used variables are to be GLOBAL'''

# Handles audio messages and converts them to text for processing

@bot.message_handler(content_types=['audio', 'voice'])
def process_audio(msg):
    audio(msg, bot)

# Bot start sequence

@bot.message_handler(commands=['start'])
def start(msg):
    clean_up()
    bot.delete_message(msg.chat.id, msg.message_id)
    start_func(msg, bot)

@bot.message_handler(func=lambda message: True)
def on_click(msg):
    if msg.text == 'Search':
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.send_message(msg.chat.id, 'Enter your query:')

    elif msg.text == 'Main':
        global offset
        global total
        global limit

        total = amount_in_table('Products')

        bot.delete_message(msg.chat.id, msg.message_id)
        main_menu_handler(bot, msg, [limit, offset, total])

    elif msg.text == 'Cart':
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.send_message(msg.chat.id, 'You are in cart')



@bot.message_handler(content_types=['photo'])
def get_photo(msg):
    markup = download_img()
    bot.reply_to(msg, 'Wonderful', reply_markup=markup)

@bot.message_handler(commands=['t'])
def test(msg):
    print('test')

'''
    It is impossible to delete
    all the history with bot
    as it doesnt see chat history
'''

@bot.callback_query_handler(func=lambda callback: True)
def callback_msg(callback):
    global offset
    global total

    total = amount_in_table('Products')
    print('Total:', total)

    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        bot.edit_message_text('Edit text', callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'previous_page':
        bot.delete_messages(callback.message.chat.id, list(range(callback.message.message_id - 10, callback.message.message_id + 1)))
        if offset < 0: offset = 0
        else: offset -= 10
        main_menu_handler(bot, callback.message, [limit, offset, total])
    elif callback.data == 'next_page':

        bot.delete_messages(callback.message.chat.id, list(range(callback.message.message_id - 10, callback.message.message_id + 1)))
        if offset < total:
            print('entered')
            offset += 10
        print(offset)
        main_menu_handler(bot, callback.message, [limit, offset, total])


bot.infinity_polling()