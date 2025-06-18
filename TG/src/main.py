import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from TG.src.modules.Optional.admin_msg_handler import AdminMessageHandler
from TG.src.modules.Templates.db_data_templates import products_template
from TG.src.config_manager import config
from TG.src.modules.Processing.DB_scripts.db_interaction import get_specific_product

from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from sub_proccess import *
from collections import defaultdict
from TG.src.modules.Processing.DB_scripts.db_semantic_search import *
from TG.src.modules.CallBack_handlers.callback_execution import *
from TG.src.modules.Processing.ML_Embeded import get_response


callback_handlers = {
    'delete': handle_delete,
    'edit': handle_edit,
    'admin_add': handle_admin_add,
    'admin_delete': handle_admin_delete,
    'entry_new': handle_entry_new,
    'entry_modify': handle_entry_modify,
    'entry_delete': handle_entry_delete,
    'add_to_cart': handle_add_to_cart,
    'more_info': handle_more_info,
    'buy_now': handle_buy_now,
    'buy_cart': handle_buy_cart,
    'do_clear_cart': handle_do_clear_cart,
}

class UserSession:
    def __init__(self):
        self.offset = 0
        self.total = 0
        self.limit = 10
        self.cart_id = None
        self.user_id = None
        self.admin = None
        self.message_ids = []
        self.text_data = []
        # Used for amin interaction handler
        self.next_step_handler = None
        self.step = 0
        self.data_collected = []

    def update_pagination(self, offset_change=0):
        self.offset += offset_change
        if self.offset < 0:
            self.offset = 0
        elif self.offset >= self.total:
            self.offset = max(0, self.total - (self.total % self.limit or self.limit))

    def add_message_id(self, msg_id):
        self.message_ids.append(msg_id)

    def add_text_data(self, text_item):
        self.text_data.append(text_item)

    def get_text_data(self):
        return self.text_data

    def clear_text_data(self):
        self.text_data = []

    async def clean_messages(self, chat_id, context):
        for msg_id in self.message_ids:
            try:
                await context.bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Error deleting message {msg_id}: {e}")
        self.message_ids = []

    def set_user_id(self, id1):
        if not self.user_id:
            self.user_id = id1

user_sessions = defaultdict(UserSession)

def get_user_session(user_id):
    return user_sessions[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_user_session(update.effective_user.id)
    session.set_user_id(update.effective_user.id)
    session.add_message_id(update.message.message_id)
    await session.clean_messages(update.effective_chat.id, context)
    session.clear_text_data()
    await MainProcess().start_func(update, context)

async def process_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_user_session(update.effective_user.id)
    session.set_user_id(update.effective_user.id)
    await MainProcess().audio(update, context)
    return

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_user_session(update.effective_user.id)
    session.set_user_id(update.effective_user.id)
    await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
    update_all_product_embeddings()

# Handles admin command interaction

async def admin_execution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_user_session(update.effective_user.id)
    session.set_user_id(update.effective_user.id)
    await session.clean_messages(update.effective_chat.id, context)
    await context.bot.send_chat_action(update.effective_chat.id, 'typing')
    session.admin = AdminMessageHandler()
    if session.admin.check_permission(update.effective_user.id):
        markup = session.admin.admin_commands()
        message = await context.bot.send_message(
            update.effective_chat.id,
            'You are an administrator',
            reply_markup=markup
        )
        session.add_message_id(message.message_id)
    else:
        await session.clean_messages(update.effective_chat.id, context)
        await MainProcess().start_func(update, context)
        session.admin = None
    await context.bot.delete_message(update.effective_chat.id, update.message.message_id)

async def on_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_user_session(update.effective_user.id)
    session.set_user_id(update.effective_user.id)
    text = update.message.text

    if session.next_step_handler == 'admin_add_input':
        await handle_admin_add_input(update.message, session, context)

    elif session.next_step_handler == 'admin_add_input':
        await handle_admin_add_input(update.message, session, context)

    elif session.next_step_handler == 'admin_add_input':
        await handle_admin_add_input(update.message, session, context)

    elif session.next_step_handler == 'admin_add_input':
        await handle_admin_add_input(update.message, session, context)
    # Keyboard functionality

    elif text == 'Search':
        await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
        search_msg = await context.bot.send_message(update.effective_chat.id, 'Enter your query:')
        session.add_message_id(search_msg.message_id)

    elif text == 'Main':
        session.total = await amount_in_table('Products')
        await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
        session.clear_text_data()
        await session.clean_messages(update.effective_chat.id, context)
        await MainMenu().main_menu_handler(
            context, update.message, session, [session.limit, session.offset, session.total]
        )

    elif text == 'Cart':
        await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
        await session.clean_messages(update.effective_chat.id, context)
        text, markup = await get_cart_data(session)
        cart_msg = await context.bot.send_message(
            update.effective_chat.id, text, parse_mode='HTML', reply_markup=markup
        )
        session.add_message_id(cart_msg.message_id)

async def callback_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text="Processing...")

    user_id = query.from_user.id
    session = get_user_session(user_id)
    session.set_user_id(user_id)
    session.total = await amount_in_table('Products')

    if query.data in ['previous_page', 'next_page']:
        await session.clean_messages(query.message.chat.id, context)
        session.clear_text_data()
        offset_change = -10 if query.data == 'previous_page' else 10
        session.update_pagination(offset_change)
        await MainMenu().main_menu_handler(
            context, query.message, session, [session.limit, session.offset, session.total]
        )

    elif query.data == 'do_return':
        await session.clean_messages(query.message.chat.id, context)
        session.clear_text_data()
        await MainMenu().main_menu_handler(
            context, query.message, session, [session.limit, session.offset, session.total]
        )

    handler = callback_handlers.get(query.data)
    if handler:
        await handler(query, session, context)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the user's message text
    user_query = update.message.text
    # Use ML_Embedded to get the best response
    results = get_response(user_query)
    if results:
        # results is a list of (question, answer) tuples, take the best one
        _, answer = results[0]
        await context.bot.send_message(update.effective_chat.id, answer)
    else:
        await context.bot.send_message(update.effective_chat.id, "Sorry, I couldn't find an answer to your question.")



MainProcess().clean_up()
application = ApplicationBuilder().token(config.get_api_key('telegram')).build()

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('test', test))
application.add_handler(CommandHandler('admin', admin_execution))
application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, process_audio))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_click))
application.add_handler(CallbackQueryHandler(callback_msg))
application.add_handler(MessageHandler(filters.ALL, unknown))

application.run_polling()