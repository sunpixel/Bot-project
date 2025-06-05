import os
from telebot import types
from sub_proccess import *
from TG.src.modules.Processing.audio import receive_audio

import telebot


bot = telebot.TeleBot('8178448433:AAEJq-zOA7dMozyVvy6UU7RbsU87FU84cPI')



# Handles audio messages and converts them to text for processing

@bot.message_handler(content_types=['audio', 'voice'])
def process_audio(msg):
    receive_audio(msg, bot)

# Bot start sequence

@bot.message_handler(commands=['start'])
def start(msg):
    clean_up()
    # Showing initial buttons
    start_func(msg, bot)

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
    bot.reply_to(msg, 'Wonderful', reply_markup=markup)




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