import telebot
from telebot import types
import sqlite3
import os
import requests
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram import WebAppInfo
import sqlite3, os
import pandas as pd


ADMIN_ID = 8479901221
# Global o'zgaruvchini aniqlash
active_chats = {}

# Bot tokeni
TOKEN = "8205339092:AAGlv2Nm_xb7ccnCkIzKkKYMyfLVqO1KkwI"
bot = telebot.TeleBot(TOKEN)

# SQLite3 bazasi bilan ulanish va jadval yaratish
db_path = 'users.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
else:
    conn = sqlite3.connect(db_path, check_same_thread=False)

cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        city TEXT
    )
''')
conn.commit()

# /start buyrug'iga javob berish uchun funksiya
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id    
    markup = InlineKeyboardMarkup()
    image_url = 'https://namozvaqti.uz/img/logo_new.png'
    
    # Rasmni yuborish
    bot.send_photo(chat_id, image_url)      
    
    # Web app URL va tugma
    web_app_url = 'https://namoz-vaqtlari-islomuz.netlify.app'   
    web_app_button = InlineKeyboardButton("🕌Namoz vaqtlari🕌", web_app=WebAppInfo(url=web_app_url))
    markup.add(web_app_button)
    
    # Foydalanuvchi ma'lumotlarini olish
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or "Familiya mavjud emas"
    username = message.from_user.username or "Username mavjud emas"
    
    # Xabarni yuborish
    welcome_message = f"Assalomu alaykum, {first_name} {last_name}!\n" \
                      f"Username: @{username}"
    
    bot.send_message(chat_id, welcome_message, reply_markup=markup)


    # Foydalanuvchi ma'lumotlarini bazaga saqlash
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()

    if result is None:
        # Foydalanuvchini bazaga qo'shish
        cursor.execute('INSERT INTO users (chat_id, first_name, last_name, username) VALUES (?, ?, ?, ?)', 
                       (chat_id, first_name, last_name, username))
        conn.commit()
        bot.send_message(chat_id, f"Salom, {first_name}! Shaharlardan birini tanlang:", reply_markup=create_inline_keyboard())
    else:
        bot.send_message(chat_id, f"Salom, {first_name}! Siz allaqachon ro'yxatdan o'tgansiz. Profilingizni ko'rish uchun\n👉/profil👈buyrug'idan foydalaning.")

# Inline tugma bosilganda ishlaydigan funksiya
@bot.callback_query_handler(func=lambda call: call.data in ["Toshkent","Angren","Andijon","Arnasoy","Ashxabod","Bekobod","Bishkek","Boysun","Buloqboshi","Burchmulla","Buxoro","Gazli","Guliston","Denov","Dehqonobod","Do'stlik","Dushanbe","Jalolobod","Jambul","Jizzax","Jomboy","Zarafshon","Zomin","Kattaqurg'on","Konibodom","Konimex","Koson","Kosonsoy","Marg'ilon","Mingbuloq","Muborak","Mo'ynoq","Navoiy","Namangan","Nukus","Nurota","Olmaota","Olot","Oltiariq","Oltinqo'l","Paxtabod","Pop","Rishton","Sayram","Samarqand","Tallimarjon","Taxtako'pir","Termiz","Tomdi","Toshhovuz","Turkiston","Turkmanobod","To'rtko'l","Uzunquduq","Urganch","Urgut","O'smat","Uchtepa","Uchquduq","Uchqo'rg'on","O'sh","O'gi'z","Farg'ona","Xazorasp","Xiva","Xonobod","Xonqa","Xo'jand","Xo'jaobod","Chimboy","Chimkent","Chortoq","Chust","Shahrijon","Sherobod","Shovot","Shumanay","Yangibozor","G'azalkent","G'allaorol","G'uzor","Qarshi","Qiziltepa","Qoravo'l","Qoravulbozor",
"Quva","Qumqo'rg'on","Qo'ng'irot","Qo'rg'ontepa","Qo'qon"
])

#bazaga saqlangan shaharni olish
def handle_city_selection(call):
    chat_id = call.message.chat.id
    city = call.data

    # Tanlangan shaharni yangilash
    cursor.execute('UPDATE users SET city = ? WHERE chat_id = ?', (city, chat_id))
    conn.commit()

    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id, f"{city} viloyati tanlandi. Profilingizni ko'rish uchun\n👉/profil👈 tugmasidan foydalaning.", reply_markup=main_keyboard())

# Viloyatni tanlash uchun tugmalar yaratish
ITEMS_PER_ROW = 2
ROWS_PER_PAGE = 8
ITEMS_PER_PAGE = ITEMS_PER_ROW * ROWS_PER_PAGE  # 16 ta shahar har sahifada

def create_inline_keyboard(page=0):
    keyboard = types.InlineKeyboardMarkup()
    cities = [
        "Toshkent","Angren","Andijon","Arnasoy","Ashxabod","Bekobod","Bishkek","Boysun",
        "Buloqboshi","Burchmulla","Buxoro","Gazli","Guliston","Denov","Dehqonobod","Do'stlik",
        "Dushanbe","Jalolobod","Jambul","Jizzax","Jomboy","Zarafshon","Zomin","Kattaqurg'on",
        "Konibodom","Konimex","Koson","Kosonsoy","Marg'ilon","Mingbuloq","Muborak","Mo'ynoq",
        "Navoiy","Namangan","Nukus","Nurota","Olmaota","Olot","Oltiariq","Oltinqo'l",
        "Paxtabod","Pop","Rishton","Sayram","Samarqand","Tallimarjon","Taxtako'pir","Termiz",
        "Tomdi","Toshhovuz","Turkiston","Turkmanobod","To'rtko'l","Uzunquduq","Urganch","Urgut",
        "O'smat","Uchtepa","Uchquduq","Uchqo'rg'on","O'sh","O'gi'z","Farg'ona","Xazorasp",
        "Xiva","Xonobod","Xonqa","Xo'jand","Xo'jaobod","Chimboy","Chimkent","Chortoq",
        "Chust","Shahrijon","Sherobod","Shovot","Shumanay","Yangibozor","G'azalkent","G'allaorol",
        "G'uzor","Qarshi","Qiziltepa","Qoravo'l","Qoravulbozor","Quva","Qumqo'rg'on",
        "Qo'ng'irot","Qo'rg'ontepa","Qo'qon"
    ]

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_cities = cities[start:end]

    # Har qator 8 tadan shahar
    for i in range(0, len(page_cities), ITEMS_PER_ROW):
        row = page_cities[i:i + ITEMS_PER_ROW]
        buttons = [types.InlineKeyboardButton(text=city, callback_data=city) for city in row]
        keyboard.row(*buttons)

    # Navigatsiya tugmalari (oldingi / keyingi)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page - 1}"))
    if end < len(cities):
        nav_buttons.append(types.InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{page + 1}"))

    if nav_buttons:
        keyboard.row(*nav_buttons)

    return keyboard
@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def paginate_cities(call):
    chat_id = call.message.chat.id
    page = int(call.data.split("_")[1])
    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=create_inline_keyboard(page))

#user
# Adminlar ro'yxati
ADMIN_IDS = [8479901221]  
# Parol
ADMIN_PASSWORD = "2212"

# --- /users buyrug‘i ---
@bot.message_handler(commands=["users"])
def show_users(message):
    # 1) Avval admin ekanligini tekshiramiz
    if message.chat.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Sizda bu buyruqni bajarish uchun ruxsat yo‘q.")
        return

    # 2) Admin bo'lsa, parol so'raymiz
    msg = bot.send_message(message.chat.id, "🔐 Iltimos, admin parolini kiriting:")
    # requester_id orqali shunchaki shu admin uchun javob olinadi
    bot.register_next_step_handler(msg, check_admin_password, requester_id=message.chat.id)

# --- Parolni tekshirish ---
def check_admin_password(message, requester_id):
    # Faqat shu so'rov yuborgan admin javob bersin
    if message.chat.id != requester_id:
        bot.send_message(message.chat.id, "❗ Bu parol so‘rovi sizga emas.")
        return

    # Parol tekshiruvi
    if message.text.strip() != ADMIN_PASSWORD:
        # noto'g'ri parol: stiker va qayta so'rash
        try:
            bot.send_sticker(
                message.chat.id,
                "CAACAgIAAxkBAAEHuJtlqUpNMiYJDmmtwSrbrhXDwRaCKgACjgADVp29Cmbq8b0MPqzULwQ"
            )
        except Exception:
            pass
        bot.send_message(message.chat.id, "❌ Parol noto‘g‘ri. Qayta urinib ko‘ring.")
        msg = bot.send_message(message.chat.id, "🔐 Parolni qayta kiriting:")
        bot.register_next_step_handler(msg, check_admin_password, requester_id=requester_id)
        return

    # Parol to'g'ri bo'lsa — usersni o'qib Excel yaratish
    try:
        cursor.execute("SELECT chat_id, first_name, last_name, username, city FROM users ORDER BY chat_id")
        users = cursor.fetchall()

        if not users:
            bot.send_message(message.chat.id, "👤 Hozircha foydalanuvchi yo‘q.")
            return

        # Excel fayl yaratish
        df = pd.DataFrame(users, columns=["chat_id", "first_name", "last_name", "username", "city"])
        excel_path = "users.xlsx"
        df.to_excel(excel_path, index=False)

        # Inline tugma bilan yuborish
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📊 Excel faylni yuklash", callback_data="download_excel")
        markup.add(btn)

        # Foydalanuvchilar soni va qisqacha preview (istalgancha o'zgartiring)
        count = len(users)
        bot.send_message(message.chat.id, f"✅ Topildi: {count} ta foydalanuvchi.\nExcelni yuklab olish uchun tugmani bosing.", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Xatolik: {e}")

# --- Excel faylni yuborish (faqat adminga) ---
@bot.callback_query_handler(func=lambda call: call.data == "download_excel")
def send_excel(call):
    # faqat ruxsatli adminlar yuklab olishi mumkin
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ Sizga ruxsat yo'q.", show_alert=True)
        return

    try:
        with open("users.xlsx", "rb") as doc:
            bot.send_document(call.message.chat.id, doc)
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, "⚠️ Excel fayl topilmadi. Avval /users buyrug‘i bilan fayl yarating.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Faylni yuborishda xato: {e}")


# /profil buyrug'iga javob berish uchun funksiya
@bot.message_handler(commands=['miniapp'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    web_app_url = 'https://namoz-vaqtlari-islomuz.netlify.app'   
    web_app_button = InlineKeyboardButton("🕌Namoz vaqtlari🕌", web_app=WebAppInfo(url=web_app_url))
    markup.add(web_app_button)
    bot.send_message(message.chat.id, "Assalomu alaykum.", reply_markup=markup)

@bot.message_handler(commands=['profil'])
@bot.message_handler(func=lambda message: message.text == "Profil")
def show_profile(message):
    chat_id = message.chat.id
    cursor.execute('SELECT first_name, last_name, username, city FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    
    if result:
        first_name, last_name, username, city = result
        profile_text = (
            f"👤 Profil Ma'lumotlari:\n\n"
            f"👤 Ism: {first_name}\n"
            f"👤 Familiya: {last_name}\n"
            f"📧 Username: {username}\n"
            f"🆔 Chat ID: {chat_id}\n"
            f"🏙 Shahar: {city or 'Tanlanmagan'}\n"
        )
        bot.send_message(chat_id, profile_text, reply_markup=edit_city_button())
    else:
        bot.send_message(chat_id, "Profil ma'lumotlari topilmadi. Iltimos,\n👉/start👈buyrug'idan foydalanib qayta ro'yxatdan o'ting.")

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Profil"), types.KeyboardButton("Namoz Vaqtlari"))
    keyboard.add(types.KeyboardButton("Info"), types.KeyboardButton("Ehson"))
    keyboard.add(types.KeyboardButton("Admin bilan aloqa"), types.KeyboardButton("Yordam 🆘"))
    return keyboard


# Shaharni tahrirlash va chiqish uchun inline tugmalar yaratish
def edit_city_button():
    keyboard = types.InlineKeyboardMarkup()
    edit_button = types.InlineKeyboardButton(text="🏙 Shaharni tahrirlash", callback_data="edit_city")
    exit_button = types.InlineKeyboardButton(text="🚪 Chiqish", callback_data="exit")
    keyboard.add(edit_button, exit_button)
    return keyboard

# Shaharni qayta tanlash uchun inline tugma bosilganda ishlaydigan funksiya
@bot.callback_query_handler(func=lambda call: call.data == "edit_city")
def edit_city(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, "Iltimos, yangi shaharni tanlang:", reply_markup=create_inline_keyboard())

# Chiqish tugmasi bosilganda foydalanuvchi ma'lumotlarini o'chirish
@bot.callback_query_handler(func=lambda call: call.data == "exit")
def exit_handler(call):
    chat_id = call.message.chat.id
    cursor.execute('DELETE FROM users WHERE chat_id = ?', (chat_id,))
    conn.commit()
    bot.send_message(chat_id, "Siz muvaffaqiyatli chiqdingiz. Ma'lumotlaringiz o'chirildi.")

# Namoz Vaqtlari tugmasi bosilganda ishlaydigan funksiya
@bot.message_handler(func=lambda message: message.text == "Namoz Vaqtlari")
def handle_namaz(message):
    chat_id = message.chat.id
    cursor.execute('SELECT city FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()

    if result:
        city = result[0]
        bot.send_message(chat_id, f"{city} viloyati uchun namoz vaqtlari variantlarini tanlang:", reply_markup=create_variant_keyboard(city))
    else:
        bot.send_message(chat_id, "Iltimos, avval shaharni tanlang.")

# Variantlarni tanlash uchun tugmani yaratish
def create_variant_keyboard(city):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="Bugungi taqvim", callback_data=f"today_{city}"),
        types.InlineKeyboardButton(text="Haftalik taqvim", callback_data=f"weekly_{city}")
    ]
    keyboard.add(*buttons)
    return keyboard

# Inline variant tugmasi bosilganda ishlaydigan funksiya
@bot.callback_query_handler(func=lambda call: call.data.startswith(("today_", "weekly_")))
def handle_variant_selection(call):
    try:
        chat_id = call.message.chat.id
        variant, city = call.data.split("_")
        if variant == "today":
            send_today_calendar(chat_id, city)
        elif variant == "weekly":
            send_weekly_calendar(chat_id, city)
    except Exception as e:
        bot.reply_to(call.message, f"Xatolik yuzaga keldi: {e}")

import requests

# Bugungi taqvimni olish
def send_today_calendar(chat_id, city):
    try:
        url = f"https://islomapi.uz/api/present/day?region={city}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "times" in data:
                times = data["times"]
                response_message = f"Bugungi namoz vaqtlari ({city} uchun):\n"
                
                # O'zgartirilgan nomlar
                names = {
                    "tong_saharlik": "Bomdod",
                    "quyosh": "Quyosh",
                    "peshin": "Peshin",
                    "asr": "Asr",
                    "shom_iftor": "Shom",
                    "hufton": "Xufton"
                }
                
                for time, value in times.items():
                    if time in names:
                        response_message += f"{names[time]}: {value}\n"
                
                # Rasm URL manzili
                photo_url = "https://namozvaqti.uz/img/logo_new.png"
                
                # Xabar va rasmni kanalga yuborish
                bot.send_photo(chat_id, photo_url, caption=response_message)
            else:
                bot.send_message(chat_id, "Namoz vaqtlari topilmadi.")
        else:
            bot.send_message(chat_id, "Namoz vaqtini olishda xato yuz berdi.")
    except Exception as e:
        bot.send_message(chat_id, f"Xatolik yuzaga keldi: {e}")

# Haftalik taqvimni olish
def send_weekly_calendar(chat_id, city):
    try:
        url = f"https://islomapi.uz/api/present/week?region={city}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                response_message = f"Haftalik namoz vaqtlari ({city} uchun):\n"
                
                # Haftaning kunlari
                weekdays = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
                
                for index, day in enumerate(data):
                    date = day["date"].split(",")[0]
                    times = day["times"]
                    weekday = weekdays[index]  # Fetch the correct weekday name
                    response_message += f"\n{weekday} ({date}):\n"
                    
                    names = {
                        "tong_saharlik": "Bomdod",
                        "quyosh": "Quyosh",
                        "peshin": "Peshin",
                        "asr": "Asr",
                        "shom_iftor": "Shom",
                        "hufton": "Xufton"
                    }
                    
                    for time, value in times.items():
                        if time in names:
                            response_message += f"{names[time]}: {value}\n"

                # Rasm URL manzili
                photo_url = "https://namozvaqti.uz/img/logo_new.png"
                
                # Xabar va rasmni kanalga yuborish
                bot.send_photo(chat_id, photo_url, caption=response_message)
            else:
                bot.send_message(chat_id, "Haftalik namoz vaqtlari topilmadi.")
        else:
            bot.send_message(chat_id, "Namoz vaqtini olishda xato yuz berdi.")
    except Exception as e:
        bot.send_message(chat_id, f"Xatolik yuzaga keldi: {e}")


# Ehson tugmasi bosilganda ishlaydigan funksiya
# --- Ehson uchun baza yaratish ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,          -- Uzcard / Humo
        card_number TEXT,
        owner_name TEXT
    )
''')
conn.commit()


# --- Ehson tugmasi ---
@bot.message_handler(func=lambda message: message.text == "Ehson")
def handle_ehson(message):
    cursor.execute("SELECT type, card_number, owner_name FROM cards")
    cards = cursor.fetchall()

    if not cards:
        ehson_text = (
            "🤲 <b>Ehson qilish — savobli amal!</b>\n\n"
            "Hozircha karta ma’lumotlari mavjud emas.\n\n"
            "📞 Savollaringiz bo‘lsa, “<b>Admin bilan aloqa</b>” tugmasini bosing."
        )
    else:
        card_texts = []
        for c in cards:
            card_texts.append(f"💳 <b>{c[0]}</b>: <code>{c[1]}</code>\n👤 {c[2]}")
        cards_str = "\n\n".join(card_texts)
        ehson_text = (
            "🤲 <b>Ehson qilish — savobli amal!</b>\n\n"
            "Alloh taolo aytadi:\n"
            "<i>“Kim Alloh yo‘lida molini sarf qilsa, u yetti boshoqli urug‘dek bo‘ladi. "
            "Har boshoqda yuzta urug‘ bo‘lur.”</i> 🌾 (Baqara, 261)\n\n"
            f"{cards_str}\n\n"
            "🕊 <i>Ehsoningiz Alloh yo‘lida qabul bo‘lsin!</i>"
        )

    markup = None
    # Faqat admin uchun tahrirlash tugmasi
    if message.chat.id in ADMIN_IDS:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✏️ Tahrirlash", callback_data="edit_cards")
        )

    bot.send_message(message.chat.id, ehson_text, parse_mode="HTML", reply_markup=markup)


# --- Admin uchun karta tahrirlash menyusi ---
@bot.callback_query_handler(func=lambda call: call.data == "edit_cards")
def edit_cards_menu(call):
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ Sizga ruxsat yo‘q.", show_alert=True)
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("➕ Karta qo‘shish", callback_data="add_card"),
        types.InlineKeyboardButton("🗑 O‘chirish", callback_data="delete_card")
    )
    bot.send_message(call.message.chat.id, "💳 Karta tahrirlash bo‘limi:", reply_markup=markup)


# --- Karta qo‘shish ---
@bot.callback_query_handler(func=lambda call: call.data == "add_card")
def add_card(call):
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ Ruxsat yo‘q.")
        return
    msg = bot.send_message(call.message.chat.id, "🔹 Karta turini kiriting (Uzcard yoki Humo):")
    bot.register_next_step_handler(msg, add_card_type)


def add_card_type(message):
    card_type = message.text.strip().capitalize()
    if card_type not in ["Uzcard", "Humo"]:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri tur. Faqat Uzcard yoki Humo kiriting:")
        bot.register_next_step_handler(msg, add_card_type)
        return

    msg = bot.send_message(message.chat.id, "💳 Karta raqamini kiriting:")
    bot.register_next_step_handler(msg, add_card_number, card_type)


def add_card_number(message, card_type):
    card_number = message.text.strip().replace(" ", "")
    if not card_number.isdigit() or len(card_number) < 12:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri karta raqami. Qayta kiriting:")
        bot.register_next_step_handler(msg, add_card_number, card_type)
        return

    msg = bot.send_message(message.chat.id, "👤 Karta egasining ismini kiriting:")
    bot.register_next_step_handler(msg, save_new_card, card_type, card_number)


def save_new_card(message, card_type, card_number):
    owner_name = message.text.strip()
    cursor.execute("INSERT INTO cards (type, card_number, owner_name) VALUES (?, ?, ?)", (card_type, card_number, owner_name))
    conn.commit()
    bot.send_message(message.chat.id, f"✅ <b>{card_type}</b> kartasi saqlandi!", parse_mode="HTML")


# --- Karta o‘chirish ---
@bot.callback_query_handler(func=lambda call: call.data == "delete_card")
def delete_card(call):
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ Ruxsat yo‘q.")
        return

    cursor.execute("SELECT id, type, card_number FROM cards")
    cards = cursor.fetchall()
    if not cards:
        bot.send_message(call.message.chat.id, "🗑 Hozircha o‘chirish uchun karta yo‘q.")
        return

    markup = types.InlineKeyboardMarkup()
    for c in cards:
        markup.add(types.InlineKeyboardButton(f"❌ {c[0]}. {c[0]} {c[1]} ({c[2][-4:]})", callback_data=f"delete_{c[0]}"))
    bot.send_message(call.message.chat.id, "Qaysi kartani o‘chirmoqchisiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def confirm_delete_card(call):
    if call.message.chat.id not in ADMIN_IDS:
        return
    card_id = int(call.data.split("_")[1])
    cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    conn.commit()
    bot.answer_callback_query(call.id, "✅ O‘chirildi.", show_alert=True)
    bot.send_message(call.message.chat.id, f"🗑 Karta ID {card_id} muvaffaqiyatli o‘chirildi.")

# Info tugmasi bosilganda ishlaydigan funksiya
@bot.message_handler(func=lambda message: message.text == "Info")
def show_info(message):
    info_message = (
        "🌙 <b>Namoz Vaqtlari Bot</b>\n\n"
        "🕌 Ushbu bot orqali siz O‘zbekistonning istalgan shaharidagi "
        "namoz vaqtlarini qulay tarzda bilib olishingiz mumkin.\n\n"
        "👤 <b>Profil bo‘limi</b> orqali:\n"
        "▫️ Shahringizni tanlang yoki o‘zgartiring\n"
        "▫️ Ismingiz va foydalanuvchi ma’lumotlarini ko‘ring\n\n"
        "⚙️ <b>Foydali imkoniyatlar:</b>\n"
        "✅ Onlayn <i>Namoz vaqtlari</i> ko‘rish\n"
        "✅ Shaxsiy profilni boshqarish\n"
        "✅ WebApp orqali islomiy sahifalarga kirish\n\n"
        "👨‍💻 <b>Muallif:</b> <a href='https://t.me/izzatbek_ibrohimov'>Ibrohimov Izzatbek</a>\n"
        "📞 <i>Telefon:</i> +998 90 298 37 01\n\n"
        "🔗 <b>Manba:</b> <a href='https://namoz-vaqtlari-islomuz.netlify.app'>Islom_uz</a>\n\n"
        "🤲 <i>Alloh sizni doimo o‘z panohida asrasin!</i>"
    )

    bot.send_message(message.chat.id, info_message, parse_mode="HTML")

# Help buyrug'iga javob berish uchun funksiya
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == "Yordam 🆘")
def show_help(message):
    help_message = (
        "📘 <b>Botdan foydalanish bo‘yicha qo‘llanma</b>\n\n"
        "Quyidagi buyruqlar orqali bot imkoniyatlaridan foydalaning 👇\n\n"
        "🚀 <b>/start</b> — Botni ishga tushirish va shaharni tanlash\n"
        "👤 <b>/profil</b> — Profil ma’lumotlaringizni ko‘rish\n"
        "🕌 <b>Namoz vaqtlari</b> — Bugungi va haftalik namoz vaqtlarini bilish\n"
        "ℹ️ <b>Info</b> — Bot haqida umumiy ma’lumot\n"
        "💰 <b>Ehson</b> — Ehson qilish uchun hisob raqamlarini ko‘rish\n"
        "❓ <b>/help</b> — Ushbu yordam sahifasini ochish\n"
        "👨‍💻 <b>Admin bilan aloqa</b> — To‘g‘ridan-to‘g‘ri admin bilan bog‘lanish\n\n"
        "💫 <i>Agar biror narsa tushunarsiz bo‘lsa, bemalol so‘rashingiz mumkin!</i>"
    )
    bot.send_message(message.chat.id, help_message, parse_mode="HTML")


# Admin ID (yagona admin misol)
ADMIN_CHAT_ID = 8479901221

# Aloqa holatlari
# active_contacts: user_id (int) -> admin_id (int)
active_contacts = {}
# admin_active: admin_id (int) -> user_id (int)
admin_active = {}

# -------------------------
# 1) Admin bilan aloqa: foydalanuvchi bosadi
# -------------------------
@bot.message_handler(func=lambda message: message.text == "Admin bilan aloqa")
def contact_admin(message):
    chat_id = message.chat.id
    cursor.execute('SELECT first_name, last_name, username, city FROM users WHERE chat_id = ?', (chat_id,))
    user_data = cursor.fetchone()

    if user_data:
        first_name, last_name, username, city = user_data
        profile_info = (
            f"Yangi aloqa so'rovi:\n"
            f"Ism: {first_name}\n"
            f"Familiya: {last_name}\n"
            f"Username: @{username}\n"
            f"Shahar: {city}\n"
            f"Chat ID: {chat_id}"
        )
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="Aloqa o'rnatish", callback_data=f"start_contact_{chat_id}")
        reject_button = types.InlineKeyboardButton(text="Aloqani rad etish", callback_data=f"reject_contact_{chat_id}")
        keyboard.add(contact_button, reject_button)

        # Adminga yuborish
        bot.send_message(ADMIN_CHAT_ID, profile_info, reply_markup=keyboard)
        bot.send_message(chat_id, "Adminga murojaatingiz yuborildi. Iltimos, javobni kuting.")
    else:
        bot.send_message(chat_id, "Profil ma'lumotlaringiz topilmadi. Iltimos, /start bilan qayta ro'yxatdan o'ting.")

# -------------------------
# 2) Admin "Aloqa o'rnatish" tugmasini bosadi
# -------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_contact_"))
def start_contact(call):
    # call.message.chat.id — bu admin chat idsi (tugma admin chatida)
    admin_id = call.message.chat.id
    user_chat_id = int(call.data.split("_")[-1])

    # Bog'lanishni saqlash
    active_contacts[user_chat_id] = admin_id
    admin_active[admin_id] = user_chat_id

    # Foydalanuvchiga va adminga xabar
    bot.send_message(user_chat_id, "Siz admin bilan bog'landingiz. Endi yozgan xabaringiz adminga yetkaziladi.")
    bot.send_message(admin_id, f"Aloqa o'rnatildi — foydalanuvchi ID: {user_chat_id}")

    # Aloqani to'xtatish tugmalari
    send_contact_stop_buttons(user_chat_id, admin_id)

# -------------------------
# 3) Stop tugmasini yuborish (foydalanuvchi va admin uchun)
# -------------------------
def send_contact_stop_buttons(user_chat_id, admin_chat_id):
    keyboard = types.InlineKeyboardMarkup()
    stop_contact_button = types.InlineKeyboardButton(
        text="Aloqani to'xtatish",
        callback_data=f"stop_contact_{user_chat_id}_{admin_chat_id}"
    )
    keyboard.add(stop_contact_button)

    bot.send_message(user_chat_id, "Aloqa o'rnatildi. Aloqani to'xtatish uchun tugmani bosing:", reply_markup=keyboard)
    bot.send_message(admin_chat_id, "Foydalanuvchi bilan aloqa o'rnatildi. Aloqani to'xtatish uchun tugmani bosing:", reply_markup=keyboard)

# -------------------------
# 4) Foydalanuvchidan kelgan xabarlar — adminga jo'natish
#    (faqat user hozir active_contacts ichida bo'lsa)
# -------------------------
@bot.message_handler(func=lambda message: message.chat.id in active_contacts)
def send_message_to_admin(message):
    user_chat_id = message.chat.id
    admin_id = active_contacts.get(user_chat_id)
    if admin_id:
        # Matn yoki media ishlashni xohlaysizmi — shu joyni kengaytiring.
        bot.send_message(admin_id,
                         f"📩 Foydalanuvchi (ID: {user_chat_id}) yubordi:\n"
                         f"👤 {message.from_user.first_name} @{message.from_user.username or 'Noma’lum'}\n\n"
                         f"{message.text}")
    else:
        bot.send_message(user_chat_id, "Hozir admin bilan aloqangiz yo'q. Iltimos, 'Admin bilan aloqa' tugmasini bosing.")

# -------------------------
# 5) Admindan kelgan xabarlar — faqat admin_active ichida bo'lsa, tegishli userga jo'natish
# -------------------------
@bot.message_handler(func=lambda message: message.chat.id in admin_active)
def send_message_to_user(message):
    admin_id = message.chat.id
    user_chat_id = admin_active.get(admin_id)
    if user_chat_id:
        bot.send_message(user_chat_id, f"Admin: {message.text}")
    else:
        bot.send_message(admin_id, "Sizda hozirda bog'langan foydalanuvchi yo'q.")

# -------------------------
# 6) Reject contact (admin rad etsa)
# -------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_contact_"))
def reject_contact(call):
    user_chat_id = int(call.data.split("_")[-1])
    bot.send_message(user_chat_id, "Afsuski, admin siz bilan aloqa o'rnatishni rad etdi.")
    bot.send_message(ADMIN_CHAT_ID, f"Aloqa rad etildi: foydalanuvchi {user_chat_id}")

# -------------------------
# 7) Stop contact callback
# -------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_contact_"))
def stop_contact(call):
    parts = call.data.split("_")
    user_chat_id = int(parts[2])
    admin_chat_id = int(parts[3])

    # O'chirish
    if user_chat_id in active_contacts:
        del active_contacts[user_chat_id]
    if admin_chat_id in admin_active:
        del admin_active[admin_chat_id]

    # Xabarlar
    try:
        bot.send_message(user_chat_id, "Aloqa to'xtatildi.")
    except Exception:
        pass
    try:
        bot.send_message(admin_chat_id, f"Foydalanuvchi (ID: {user_chat_id}) bilan aloqa to'xtatildi.")
    except Exception:
        pass

# -------------------------
# 8) ISLOMIY AVTOJAVOB — oxirida ro'yxatga olinadi va faqat ACTIVE BO'LМАГАН foydalanuvchilarga javob beradi
# -------------------------
@bot.message_handler(func=lambda message: (
    # text bo'lishi kerak va foydalanuvchi hozir admin bilan bog'langan bo'lmasin
    isinstance(message.text, str)
    and (message.chat.id not in active_contacts)
    and (message.chat.id not in admin_active)  # adminlar uchun ham avtomatik javob chiqmasin
))
def islamic_auto_reply(message):
    user_text = message.text.lower().strip()

    greetings = ["salom", "assalomu alaykum", "assalamu alaykum", "salom aleykum", "va alaykum assalom"]
    how_are_you = ["yaxshimisiz", "qandaysiz", "ishlar qalay", "ahvol", "ahvollar", "nima gap"]
    thanks = ["rahmat", "raxmat", "katta rahmat", "minnatdorman", "barakalla"]
    help_words = ["yordam", "savol", "so'rov", "so'ramoqchiman", "menga yordam", "savolim bor"]
    dua_words = ["duo", "duo qiling", "duo qib bering", "duolar"]
    allah_words = ["allah", "rozzaq", "rahmon", "rahim", "astag‘firulloh", "subhanallah", "alhamdulillah", "bismillah"]

    responses = {
        "greeting": [
            "Va alaykum assalom va rohmatullohi va barokatuh! 🌙",
            "Assalomu alaykum, Alloh sizni rahmatiga olsin 🤲",
            "Salom! Tinchlik va baraka sizga bo‘lsin ☪️",
            "Va alaykum assalom! Bugun qalbingiz tinchlikda bo‘lsin inshaAlloh 💫"
        ],
        "how_are_you": [
            "Alhamdulillah, yaxshiman 😊 Sizda ham hammasi joyidami?",
            "Shukr, Alloh fazlida tinchlik 🌿 Sizning kayfiyatingiz qanday?",
            "Alhamdulillah, har doim yaxshilikdaman. Siz-chi, ahvollaringiz yaxshimi?",
            "Shukrlar bo‘lsin, Alloh taolo baraka bersin sizga ham 🤍"
        ],
        "thanks": [
            "Alloh sizdan rozi bo‘lsin 🤲",
            "Rahmat, sizga ham duolarimni yuboraman 🌸",
            "Shukr, har yaxshilik Allohdandir 🌿",
            "Barakalla, Alloh sizning amallaringizni qabul qilsin 🌺"
        ],
        "help": [
            "Albatta, yordam berishga tayyorman. Savolingizni yozing 🕋",
            "Yordam kerakmi? Savolingizni aniq yozing, imkon qadar islomiy manbalardan javob beraman 📖",
            "Marhamat, savolingizni yuboring. Bilganimcha tushuntiraman inshaAlloh 🤍",
            "Allohning izni bilan sizga yordam beraman. Nima haqida so‘ramoqchisiz? ☪️"
        ],
        "dua": [
            "InshaAllOh, siz uchun ham duo qilaman 🤲",
            "Alloh taolo niyatlaringizni ijobat qilsin 🌸",
            "Har bir duoda sizni ham eslab o‘tamiz, Alloh baraka bersin 🌿",
            "Duo qalbning so‘zi — siz uchun ham tinchlik, baraka va muhabbat so‘rayman 💫"
        ],
        "allah": [
            "Subhanalloh! 🌙 Allohni zikr etish qalbni sokin qiladi.",
            "Alhamdulillah, Alloh sizni rahmatida saqlasin 🤲",
            "Alloh sizni o‘z panohida asrasin va hayotingizni baraka bilan to‘ldirsin ☪️",
            "Allohni eslagan qalb hech qachon yolg‘iz qolmaydi 💖"
        ],
        "unknown": [
            "Alloh sizga yaxshilik bersin 🌙 Savolingizni aniqroq yozsangiz, to‘liqroq javob bera olaman.",
            "Tushundim, lekin iltimos, savolingizni biroz batafsilroq yozing 🕋",
            "Bu masala haqida aniqlik kiritaylik, Alloh izni bilan sizga to‘g‘ri yo‘lni ko‘rsatamiz 🤍",
            "Yaxshi fikr, keling, birgalikda islomiy nuqtai nazardan ko‘rib chiqamiz 🌿"
        ]
    }

    if any(word in user_text for word in greetings):
        reply = random.choice(responses["greeting"])
    elif any(word in user_text for word in how_are_you):
        reply = random.choice(responses["how_are_you"])
    elif any(word in user_text for word in thanks):
        reply = random.choice(responses["thanks"])
    elif any(word in user_text for word in help_words):
        reply = random.choice(responses["help"])
    elif any(word in user_text for word in dua_words):
        reply = random.choice(responses["dua"])
    elif any(word in user_text for word in allah_words):
        reply = random.choice(responses["allah"])
    else:
        reply = random.choice(responses["unknown"])

    bot.reply_to(message, reply)

# Botni ishga tushirish
import time
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5) 

