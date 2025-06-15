from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from TG.src.modules.Optional.admin_db_interaction import *

class AdminMessageHandler:
    def __init__(self):
        self.is_admin = False
        self.allowed_commands = []

    def admin_commands(self):
        if self.is_admin:
            buttons = []
            if 'add_admin' in self.allowed_commands:
                buttons.append([InlineKeyboardButton('Add Admin', callback_data='admin_add')])
            if 'delete_admin' in self.allowed_commands:
                buttons.append([InlineKeyboardButton('Delete Admin', callback_data='admin_delete')])
            if 'new_entry' in self.allowed_commands:
                buttons.append([InlineKeyboardButton('New Entry', callback_data='entry_new')])
            if 'modify_entry' in self.allowed_commands:
                buttons.append([InlineKeyboardButton('Modify Entry', callback_data='entry_modify')])
            if 'delete_entry' in self.allowed_commands:
                buttons.append([InlineKeyboardButton('Delete Entry', callback_data='entry_delete')])
            return InlineKeyboardMarkup(buttons)
        return None

    def admin_add(self, user_data):
        if self.is_admin and 'add_admin' in self.allowed_commands:
            add_new_admin(user_data)
            return 'admin added'
        else:
            return 'permission denied'

    def admin_delete(self, user_data):
        if self.is_admin and 'delete_admin' in self.allowed_commands:
            delete_admin(user_data)
            return 'admin deleted'
        else:
            return 'permission denied'

    def check_permission(self, user_id: int):
        admin = check_existence('admins', 'user_id', user_id)
        if admin:
            print('Entered permission_check')
            self.is_admin = True
            self.allowed_commands = admin[2].replace(' ', '').split(',')
            print(self.allowed_commands)
            return True
        return False