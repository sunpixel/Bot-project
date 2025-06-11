import os
from telebot import types
from sub_proccess import *
from TG.src.config_manager import config
import telebot

bot = telebot.TeleBot(config.get_api_key('telegram'))



# Handles audio messages and converts them to text for processing

@bot.message_handler(content_types=['audio', 'voice'])
def process_audio(msg):
    audio(msg, bot)

# Bot start sequence

@bot.message_handler(commands=['start'])
def start(msg):
    clean_up()
    start_func(msg, bot)
    bot.delete_message(msg.chat.id, msg.message_id -1)

@bot.message_handler(func=lambda message: True)
def on_click(msg):
    if msg.text == 'Search':
        bot.send_message(msg.chat.id, 'Enter your query:')
    elif msg.text == 'Main':
        bot.send_message(msg.chat.id, 'Main page')
    elif msg.text == 'Cart':
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
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        bot.edit_message_text('Edit text', callback.message.chat.id, callback.message.message_id)


bot.infinity_polling()