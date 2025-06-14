from torch._dynamo import callback

from TG.src.modules.Optional.admin_msg_handler import *


def handle_admin_add(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id, 'Please provide user_id or username and command list,'
                                                     'everything should be separated by whitespace')
    session.add_message_id(msg.message_id)
    bot.register_next_step_handler(msg, handle_admin_add_input, session, bot)

def handle_admin_add_input(message, session, bot):
    parts = [p.strip() for p in message.text.split()]
    user_id = int(parts[0])
    commands = parts[1:]
    bot.delete_message(message.chat.id, message.id)
    session.clean_messages(message.chat.id)
    print(session.admin.admin_add([user_id, commands]))


def handle_admin_delete(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Enter admin user_id to delete')
    session.add_message_id(msg.message_id)
    bot.register_next_step_handler(msg, handle_admin_delete_input, session, bot)

def handle_admin_delete_input(message, session, bot):
    try:
        bot.delete_message(message.chat.id, message.id)
        session.clean_messages(message.chat.id)
        user_id = int(message.text)
        session.admin.admin_delete(user_id)
    except:
        pass


def handle_entry_new(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Try to add an entry')
    session.add_message_id(msg.message_id)


def handle_entry_delete(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    bot.delete_message(callback.message.chat.id, callback.message.id)
    msg = bot.send_message(callback.message.chat.id,
                           'To delete an entry provide'
                           'name or id')
    session.add_message_id(msg.message_id)


def handle_entry_delete_input(message, session, bot):
    try:
        bot.delete_message(message.chat.id, message.id)
        session.clean_messages(message.chat.id)
        try:
            entry_id = int(message.text)
            session.admin.delete_entry(entry_id, 'id')
        except:
            entry_name = message.text.strip()
            session.admin.delete_entry(entry_name, 'name')
    except:
        pass

def handle_entry_modify(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    admin = AdminMessageHandler()
    msg = bot.send_message(callback.message.chat.id,
                           'Try to modify an entry')
    session.add_message_id(msg.message_id)
    admin = None

def handle_edit(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    if session.text_data:
        new_text = f"Edited: {session.text_data[0]}"  # Using first item as example
        bot.edit_message_text(new_text, callback.message.chat.id, callback.message.message_id)


def handle_delete(callback, session, bot):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)


'''
    elif callback.data == 'admin_add':
        session.clean_messages(callback.message.chat.id)
        msg = bot.send_message(callback.message.chat.id,
                               'Try to make an admin')
        session.add_message_id(msg.message_id)

    elif callback.data == 'admin_delete':
        session.clean_messages(callback.message.chat.id)
        msg = bot.send_message(callback.message.chat.id,
                               'Try to delete an admin')
        session.add_message_id(msg.message_id)

    elif callback.data == 'entry_new':
        session.clean_messages(callback.message.chat.id)
        msg = bot.send_message(callback.message.chat.id,
                               'Try to add an entry')
        session.add_message_id(msg.message_id)

    elif callback.data == 'entry_modify':
        session.clean_messages(callback.message.chat.id)
        msg = bot.send_message(callback.message.chat.id,
                               'Try to modify an entry')
        session.add_message_id(msg.message_id)

    elif callback.data == 'entry_delete':
        session.clean_messages(callback.message.chat.id)
        msg = bot.send_message(callback.message.chat.id,
                               'Try to delete an entry')
        session.add_message_id(msg.message_id)



'''