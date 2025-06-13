import os
import telebot
from telebot import types
from TG.src.modules.Templates.db_data_templates import products_template
from sub_proccess import *
from TG.src.config_manager import config
from collections import defaultdict

bot = telebot.TeleBot(config.get_api_key('telegram'))


class UserSession:
    def __init__(self):
        # Pagination control
        self.offset = 0
        self.total = 0
        self.limit = 10

        # Message ID tracking (original functionality)
        self.message_ids = []

        # Separate text data storage (new functionality)
        self.text_data = []  # Can be list or dict depending on needs

    def update_pagination(self, offset_change=0):
        self.offset += offset_change
        if self.offset < 0:
            self.offset = 0
        elif self.offset >= self.total:
            self.offset = max(0, self.total - (self.total % self.limit or self.limit))

    def add_message_id(self, msg_id):
        """Original message tracking"""
        self.message_ids.append(msg_id)

    def add_text_data(self, text_item):
        """Separate text data storage"""
        self.text_data.append(text_item)

    def get_text_data(self):
        """Retrieve stored text data"""
        return self.text_data

    def clear_text_data(self):
        """Clear text storage"""
        self.text_data = []

    def clean_messages(self, chat_id):
        """Delete all tracked messages"""
        for msg_id in self.message_ids:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Error deleting message {msg_id}: {e}")
        self.message_ids = []


user_sessions = defaultdict(UserSession)


def get_user_session(user_id):
    return user_sessions[user_id]


@bot.message_handler(commands=['start'])
def start(msg):
    session = get_user_session(msg.from_user.id)
    session.add_message_id(msg.message_id)
    session.clean_messages(msg.chat.id)
    session.clear_text_data()
    bot.delete_message(msg.chat.id, msg.message_id)
    start_func(msg, bot)


@bot.message_handler(func=lambda message: True)
def on_click(msg):
    session = get_user_session(msg.from_user.id)

    if msg.text == 'Search':
        bot.delete_message(msg.chat.id, msg.message_id)
        search_msg = bot.send_message(msg.chat.id, 'Enter your query:')
        session.add_message_id(search_msg.message_id)

    elif msg.text == 'Main':
        session.total = amount_in_table('Products')
        bot.delete_message(msg.chat.id, msg.message_id)
        session.clean_messages(msg.chat.id)

        # Get both lists from main_menu_handler
        msg_ids, text_items = main_menu_handler(bot, msg, [session.limit, session.offset, session.total])

        # Store them separately
        for msg_id in msg_ids:
            session.add_message_id(msg_id)
        for text_item in text_items:
            session.add_text_data(text_item)

    elif msg.text == 'Cart':
        bot.delete_message(msg.chat.id, msg.message_id)
        cart_msg = bot.send_message(msg.chat.id, 'You are in cart')
        session.add_message_id(cart_msg.message_id)


@bot.callback_query_handler(func=lambda callback: True)
def callback_msg(callback):
    user_id = callback.from_user.id
    session = get_user_session(user_id)

    session.total = amount_in_table('Products')

    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == 'edit':
        # Example usage of text data (modify as needed)
        if session.text_data:
            new_text = f"Edited: {session.text_data[0]}"  # Using first item as example
            bot.edit_message_text(new_text, callback.message.chat.id, callback.message.message_id)

    elif callback.data in ['previous_page', 'next_page']:
        session.clean_messages(callback.message.chat.id)
        session.clear_text_data()

        offset_change = -10 if callback.data == 'previous_page' else 10
        session.update_pagination(offset_change)

        msg_ids, text_items = main_menu_handler(bot, callback.message, [session.limit, session.offset, session.total])

        for msg_id in msg_ids:
            session.add_message_id(msg_id)
        for text_item in text_items:
            session.add_text_data(text_item)

    elif callback.data == 'more_info':
        msg_id = callback.message.message_id
        db_search = session.text_data[session.message_ids.index(msg_id)]
        data = get_specific_data(db_search)
        i = 0
        for key in products_template.keys():
            products_template[key] = data[i]
            i += 1
        session.clean_messages(callback.message.chat.id)
        text = ''
        for key, value in products_template.items():
            text += f"{key}: {value}\n"
        message = bot.send_message(callback.message.chat.id, text)
        session.add_message_id(message.message_id)


bot.infinity_polling()