import os
import aiosqlite
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, Update
)
from telegram.constants import ParseMode
from io import BytesIO
from TG.src.modules.Processing.audio import receive_audio, check_audio
from TG.src.config_manager import config
from TG.src.modules.Processing.DB_scripts.db_interaction import cart_data_retrival, ensure_cart_created

async def db_connection():
    return await aiosqlite.connect(config.db_path)

class MainProcess:
    def __init__(self):
        pass

    @staticmethod
    def clean_up():
        down_dir = os.path.abspath(os.path.join(config.data_path, 'Downloads'))
        upld_dir = os.path.abspath(os.path.join(config.data_path, 'Uploads'))
        downloads = os.listdir(down_dir)
        uploads = os.listdir(upld_dir)

        array = [[downloads, down_dir], [uploads, upld_dir]]

        for items in array:
            for item in items[0]:
                os.remove(os.path.join(items[1], item))

    @staticmethod
    async def start_func(update: Update, context):
        markup = ReplyKeyboardMarkup(
            [
                [KeyboardButton('Search')],
                [KeyboardButton('Main'), KeyboardButton('Cart')]
            ],
            resize_keyboard=True
        )

        await get_create_user([update.effective_user.id, update.effective_user.username])

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Hi',
            reply_markup=markup
        )
        return message.message_id

    @staticmethod
    async def audio(update: Update, context):
        MainProcess().clean_up()
        data = await receive_audio(update, context)
        v1 = await check_audio(data[0], update, context, data[1])
        with open(v1, 'rb') as voice_file:
            try:
                message = await context.bot.send_voice(update.effective_chat.id, voice_file)
            except Exception as e:
                await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("How to Allow Voice", url="https://core.telegram.org/bots/faq#voice-messages")],
                    [InlineKeyboardButton("Check Privacy Settings", url="https://telegram.org/faq#privacy")],
                    [InlineKeyboardButton("Contact Support", url="https://telegram.org/support")]
                ])
                print(e)
                message = await context.bot.send_message(
                    update.effective_chat.id,
                    "<b>An error has occurred while sending your voice message.</b>\n\n"
                    "Please use the buttons below to get help with fixing common issues:",
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML
                )
        return message.message_id

async def db_select_all_data(table):
    conn = await db_connection()
    cursor = await conn.cursor()
    await cursor.execute(f'''
    SELECT * FROM {table}
    ''')
    data = await cursor.fetchall()
    await conn.close()
    print(data)

async def get_create_user(user_data):
    conn = await db_connection()
    cursor = await conn.cursor()

    user_id = int(user_data[0])
    username = str(user_data[1])

    await cursor.execute('''
    SELECT * FROM Users WHERE user_id = ?
    ''', (user_id,))

    user = await cursor.fetchone()

    if not user:
        await cursor.execute('''
        INSERT INTO Users (
        user_id,
        username
        ) VALUES (?, ?)
        ''', (user_id, username))
        await conn.commit()
    await conn.close()

def download_img():
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Go to URL', url='https://ya.ru')],
        [InlineKeyboardButton('Edit text', callback_data='edit'),
         InlineKeyboardButton('Delete photo', callback_data='delete')]
    ])
    return markup

class MainMenu:
    def __init__(self):
        pass

    @staticmethod
    async def main_menu_data(limit=10, offset=0):
        conn = await db_connection()
        cursor = await conn.cursor()
        await cursor.execute(
            'SELECT * FROM Products LIMIT ? OFFSET ?', (limit, offset)
        )
        data = await cursor.fetchall()
        display_data = []
        for row in data:
            data = {'name': row[2], 'price': row[9]}
            display_data.append(data)
        await conn.close()
        return display_data

    @staticmethod
    def main_menu_msg():
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('🛒 Add to Cart 🛒', callback_data='add_to_cart'),
                InlineKeyboardButton('🔥 Buy Now 🔥', callback_data='buy_now')
            ],
            [InlineKeyboardButton('❓ More Info ❓', callback_data='more_info')]
        ])
        return markup

    @staticmethod
    def extra_menu_message(total, limit, offset):
        buttons = []
        if offset // 10 != 0:
            buttons.append(InlineKeyboardButton('⏪ Previous page', callback_data='previous_page'))
        if total - offset >= limit:
            buttons.append(InlineKeyboardButton('Next page ⏩', callback_data='next_page'))
        markup = InlineKeyboardMarkup([buttons] if buttons else [])
        return markup

    async def main_menu_handler(self, context, update, session, data_set_atr):
        limit = data_set_atr[0]
        offset = data_set_atr[1]
        total = data_set_atr[2]

        menu_data = await MainMenu.main_menu_data(limit, offset)
        for data in menu_data:

            image_stream = await send_image_blob(data['name'])

            text = f"{data['name']}\n" + "—" * 10 + f"\nPrice: {data['price']}"
            markup = self.main_menu_msg()
            if image_stream:
                message= await context.bot.send_photo(
                    chat_id=update.chat.id,
                    photo=image_stream,
                    caption=text,
                    reply_markup=markup
                )
                session.add_text_data(message.caption)
            else:
                place_holder_path = os.path.abspath(os.path.join(config.data_path, 'DataBase', 'No_Image.jpeg'))
                print(place_holder_path)
                message= await context.bot.send_photo(
                    chat_id=update.chat.id,
                    photo=open(place_holder_path, "rb"),
                    caption=text,
                    reply_markup=markup
                )
                session.add_text_data(message.caption)
                session.add_text_data(message.text)

            session.add_message_id(message.message_id)

        markup = self.extra_menu_message(total, limit, offset)
        message = await context.bot.send_message(
            update.chat.id,
            '-' * 20,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
        session.add_message_id(message.message_id)

async def amount_in_table(table_name):
    conn = await db_connection()
    cursor = await conn.cursor()
    await cursor.execute(f'''
        SELECT count(*) FROM {table_name}
    ''')
    row = await cursor.fetchone()
    total = int(row[0]) if row else 0
    await conn.close()
    if total:
        return total
    return 0

async def get_cart_data(session):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('✅🛒 Buy 🛒✅', callback_data='buy_cart')],
        [InlineKeyboardButton('🗑️ Clear cart 🗑️', callback_data='do_clear_cart')],
        [InlineKeyboardButton('⏪ Back ⏪', callback_data='do_return')]
    ])
    if session.cart_id:
        data = await cart_data_retrival(session.cart_id)
    else:
        await ensure_cart_created(session.user_id, session)
        data = await cart_data_retrival(session.cart_id)

    cart_message = "<b>🛍️ Your Shopping Cart 🛍️</b>\n<pre>\n"
    for item, qty, price in data:
        total = price * qty
        cart_message += f"{item:<25} │ ×{qty:<2} │ ₽  {total:>7.2f}\n"

    grand_total = sum(price * qty for _, qty, price in data)
    cart_message += f"\n{'GRAND TOTAL:':<25}         ₽   {grand_total:>7.2f}</pre>"
    return cart_message, markup


async def send_image_blob(name):
    conn = await db_connection()
    cursor = await conn.cursor()

    await cursor.execute('''
        SELECT image FROM Products
        WHERE name = ?
    ''', (name,))

    try:
        image = await cursor.fetchone()
        if image[0] is not None:
            image_blob = image[0]
            image_stream = BytesIO(image_blob)
            # Telegram requires a name for all sent files
            image_stream.name = f"{name.strip()}.jpeg"
        else:
            place_holder_path = os.path.abspath(
                os.path.join(config.data_path, 'DataBase', 'No_Image.jpeg'))
            with open(place_holder_path, 'rb') as file:
                image_blob = file.read()
            image_stream = BytesIO(image_blob)
            # Telegram requires a name for all sent files
            image_stream.name = f"{name.strip()}.jpeg"
        return image_stream


    except Exception as e:
        print(f'Image retrival error: {e}')
        return None

