import os
import telebot
from telebot import types

from TG.src.modules.Optional.admin_msg_handler import AdminMessageHandler
from TG.src.modules.Templates.db_data_templates import products_template
from sub_proccess import *
from TG.src.config_manager import config
from collections import defaultdict
from TG.src.modules.Processing.DB_scripts.db_semantic_search import *
from TG.src.modules.CallBack_handlers.callback_execution import *

bot = telebot.TeleBot(config.get_api_key('telegram'))


callback_handlers = {
    'delete': handle_delete,
    'edit': handle_edit,
    'admin_add': handle_admin_add,
    'admin_delete': handle_admin_delete,
    'entry_new': handle_entry_new,
    'entry_modify': handle_entry_modify,
    'entry_delete': handle_entry_delete,
}

class UserSession:
    def __init__(self):
        # Pagination control
        self.offset = 0
        self.total = 0
        self.limit = 10

        self.admin = None

        self.message_ids = []
        self.text_data = []

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
    #bot.delete_message(msg.chat.id, msg.message_id)
    MainProcess().start_func(msg, bot)

@bot.message_handler(content_types=['audio', 'voice'])
def process_audio(msg):
    MainProcess().audio(msg, bot)


@bot.message_handler(commands=['test'])
def test(msg):
    session = get_user_session(msg.from_user.id)
    bot.delete_message(msg.chat.id, msg.message_id)
    update_all_product_embeddings()

@bot.message_handler(commands=['admin'])
def admin_execution(msg):
    session = get_user_session(msg.from_user.id)
    session.clean_messages(msg.chat.id)
    bot.send_chat_action(msg.chat.id, 'typing')
    session.admin = AdminMessageHandler()
    if session.admin.check_permission(msg.from_user.id):
        markup = session.admin.admin_commands()
        message = bot.send_message(msg.chat.id, 'You are an administrator',
                            reply_markup=markup)
        session.add_message_id(message.message_id)
    else:
        message = bot.send_message(msg.chat.id, 'Permission Denied')
        session.add_message_id(message.message_id)
        session.clean_messages(msg.chat.id)
        MainProcess().start_func(msg, bot)
        session.admin = None
    bot.delete_message(msg.chat.id, msg.message_id)


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
        msg_ids, text_items = MainMenu().main_menu_handler(bot, msg, [session.limit, session.offset, session.total])

        # Store them separately
        for msg_id in msg_ids:
            session.add_message_id(msg_id)
        for text_item in text_items:
            session.add_text_data(text_item)

    elif msg.text == 'Cart':
        bot.delete_message(msg.chat.id, msg.message_id)
        cart_msg = bot.send_message(msg.chat.id, 'You are in cart')
        session.add_message_id(cart_msg.message_id)


# Better left at the bottom for easy access

@bot.callback_query_handler(func=lambda callback: True)
def callback_msg(callback):
    user_id = callback.from_user.id
    session = get_user_session(user_id)

    session.total = amount_in_table('Products')

    if callback.data in ['previous_page', 'next_page']:
        session.clean_messages(callback.message.chat.id)
        session.clear_text_data()

        offset_change = -10 if callback.data == 'previous_page' else 10
        session.update_pagination(offset_change)

        msg_ids, text_items = MainMenu().main_menu_handler(bot, callback.message, [session.limit, session.offset, session.total])

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

    handler = callback_handlers.get(callback.data)
    if handler:
        handler(callback, session, bot)


bot.infinity_polling()
