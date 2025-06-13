from telebot import types
from TG.src.modules.Optional.admin_db_interaction import *

class AdminMessageHandler:
	def __init__(self):
		self.types = types
		self.is_admin = False
		self.allowed_commands = []

	def admin_commands(self):

		if self.is_admin:
			markup = types.InlineKeyboardMarkup()
			if 'add_admin' in self.allowed_commands:
				admin_add =     types.InlineKeyboardButton('Add Admin', callback_data='admin_add')
				markup.add(admin_add, row_width = 2)
			if 'delete_admin' in self.allowed_commands:
				admin_delete =  types.InlineKeyboardButton('Delete Admin', callback_data='admin_delete')
				markup.add(admin_delete, row_width = 2)
			if 'new_entry' in self.allowed_commands:
				entry_new =     types.InlineKeyboardButton('New Entry', callback_data='entry_new')
				markup.add(entry_new, row_width = 2)
			if 'modify_entry' in self.allowed_commands:
				entry_modify =  types.InlineKeyboardButton('Modify Entry', callback_data='entry_modify')
				markup.add(entry_modify, row_width = 2)
			if 'delete_entry' in self.allowed_commands:
				entry_delete =  types.InlineKeyboardButton('Delete Entry', callback_data='entry_delete')
				markup.add(entry_delete, row_width = 2)

			return markup

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
