def handle_admin_add(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Try to make an admin')
    session.add_message_id(msg.message_id)

def handle_admin_delete(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Try to delete an admin')
    session.add_message_id(msg.message_id)

def handle_entry_new(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Try to add an entry')
    session.add_message_id(msg.message_id)

def handle_entry_delete(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Try to delete an entry')
    session.add_message_id(msg.message_id)

def handle_entry_modify(callback, session, bot):
    session.clean_messages(callback.message.chat.id)
    msg = bot.send_message(callback.message.chat.id,
                           'Try to modify an entry')
    session.add_message_id(msg.message_id)

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