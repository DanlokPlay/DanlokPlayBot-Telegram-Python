from config import API_TOKEN, DEVELOPER_ID, LOG_FILE, TEMP_LOG_FILE, CHECK_FOLDER, INFO_FOLDER, INFORMATION_FILE, UPDATE_FOLDER, BASE_URL
from random import randint
import random


import re
import os
import glob

import telebot
from telebot import types

import threading
import schedule

from datetime import datetime
import pytz
TIMEZONE = pytz.timezone('Europe/Moscow')

import requests
import gzip
import json

token = API_TOKEN
bot = telebot.TeleBot(token)

import time

print('OK')


# Пример функции, которая выводит текущее время в нужной таймзоне
def get_current_time_in_timezone():
    now = datetime.now(TIMEZONE)
    return now.strftime("%Y-%m-%d %H:%M:%S")
# Вывод времени при старте бота
current_time = get_current_time_in_timezone()
print(f"Текущее время: {current_time}")


"""
def is_chat_admin(bot, chat_id, user_id):
    try:
        chat_admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in chat_admins)
    except Exception as e:
        print(f"Не удалось получить список администраторов: {e}")
        return False

def check_access(chat_id, command):
    with sqlite3.connect('chat_servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT {command} FROM access_to_commands WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return result and result[0]

def get_command_cooldown(chat_id, command):
    command_column = f'cd_{command}'
    with sqlite3.connect('chat_servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT {command_column} FROM command_cooldowns WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return result[0] if result else 5  # Значение КД по умолчанию 5 секунд

def set_command_cooldown(chat_id, command, cooldown_duration):
    command_column = f'cd_{command}'
    with sqlite3.connect('chat_servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE command_cooldowns
            SET {command_column} = ?
            WHERE chat_id = ?
        ''', (cooldown_duration, chat_id))
        conn.commit()

last_command_execution_time = {}

def cool_down(message, command):
    chat_id = message.chat.id
    current_time = datetime.now()

    command_cooldown = get_command_cooldown(chat_id, command)

    if chat_id < 0:
        if chat_id not in last_command_execution_time:
            last_command_execution_time[chat_id] = {}

        if command in last_command_execution_time[chat_id]:
            time_since_last_execution = (current_time - last_command_execution_time[chat_id][command]).total_seconds()
            remaining_cooldown = command_cooldown - time_since_last_execution
            if remaining_cooldown > 0:
                bot.reply_to(message, f"Подождите еще {int(remaining_cooldown)} секунд перед использованием этой команды.")
                return False

        last_command_execution_time[chat_id][command] = current_time

    return True
"""

def debug_message(message, additional_text):
    chat_name = message.chat.title if message.chat.title else message.chat.username
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    notification_text = f'{additional_text} @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
    
    # Получаем текущее время по МСК
    current_time_msk = get_current_time_in_timezone()

    # Отправка сообщения разработчику
    if additional_text == 'Спасибо от ':
        bot.send_message(DEVELOPER_ID, f'Спасибо от @{username}')

    # Запись в лог-файл
    log_entry = f'{current_time_msk} - {notification_text}\n'  # Используем текущее время по МСК
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)
    with open(TEMP_LOG_FILE, 'a', encoding='utf-8') as temp_log_file:
        temp_log_file.write(log_entry)




import sqlite3

# Регистрация обработчика сообщений
#@bot.message_handler(func=lambda message: message)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    chat_name = message.chat.title if message.chat.title else None
    creator_id = message.from_user.id
    creator_username = message.from_user.username

    # Все пользователи
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                surname TEXT,
                sanctions TEXT DEFAULT 'Нет',
                survival_points INTEGER DEFAULT 0,
                last_time TEXT DEFAULT ''
            )
        ''')

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        existing_user = cursor.fetchone()

        current_time = datetime.now(TIMEZONE).strftime("%H:%M:%S, %d:%m:%Y")

        if existing_user:
            if existing_user[1] != username:
                cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
            if message.from_user.first_name:
                cursor.execute('UPDATE users SET name = ? WHERE id = ?', (message.from_user.first_name, user_id))
            if message.from_user.last_name:
                cursor.execute('UPDATE users SET surname = ? WHERE id = ?', (message.from_user.last_name, user_id))
            
            cursor.execute('UPDATE users SET last_time = ? WHERE id = ?', (current_time, user_id))
            conn.commit()
        else:
            cursor.execute('''
            INSERT INTO users (id, username, name, surname, last_time) VALUES (?, ?, ?, ?, ?)''', (user_id, username, message.from_user.first_name, message.from_user.last_name, current_time))
            conn.commit()
            print(f"Добавлен новый пользователь: {user_id}")
            debug_message(message, f"Добавлен новый пользователь: {user_id}")


"""
    # Если сообщение не в Личных сообщениях
    if message.chat.type != 'private':
        with sqlite3.connect('chat_servers.db') as conn:
            cursor = conn.cursor()

            try:
                admins = bot.get_chat_administrators(chat_id)
                admin_ids = ",".join([str(admin.user.id) for admin in admins])
                admin_usernames = ",".join([admin.user.username for admin in admins if admin.user.username is not None])
            except Exception as e:
                print(f"Не удалось получить список администраторов: {e}")
                admin_ids = ""
                admin_usernames = ""

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    chat_name TEXT,
                    creator_id INTEGER,
                    creator_username TEXT,
                    admin_ids TEXT,
                    admin_usernames TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_to_commands (
                    chat_id INTEGER PRIMARY KEY,
                    chat_name TEXT,
                    thank_you BOOLEAN DEFAULT TRUE,
                    info_custom BOOLEAN DEFAULT TRUE,
                    admin BOOLEAN DEFAULT TRUE,
                    developer BOOLEAN DEFAULT TRUE,
                    code BOOLEAN DEFAULT TRUE,
                    codes BOOLEAN DEFAULT TRUE,
                    coin BOOLEAN DEFAULT TRUE,
                    upload_photo BOOLEAN DEFAULT TRUE,
                    photo BOOLEAN DEFAULT TRUE,
                    video BOOLEAN DEFAULT TRUE,
                    kef BOOLEAN DEFAULT TRUE,
                    all_updates BOOLEAN DEFAULT TRUE,
                    last_update BOOLEAN DEFAULT TRUE,
                    top BOOLEAN DEFAULT TRUE,
                    hey BOOLEAN DEFAULT TRUE,
                    raids BOOLEAN DEFAULT TRUE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_cooldowns (
                    chat_id INTEGER PRIMARY KEY,
                    chat_name TEXT,
                    cd_thank_you INTEGER DEFAULT 5,
                    cd_info_custom INTEGER DEFAULT 5,
                    cd_admin INTEGER DEFAULT 5,
                    cd_developer INTEGER DEFAULT 5,
                    cd_code INTEGER DEFAULT 5,
                    cd_codes INTEGER DEFAULT 5,
                    cd_coin INTEGER DEFAULT 5,
                    cd_upload_photo INTEGER DEFAULT 5,
                    cd_photo INTEGER DEFAULT 5,
                    cd_video INTEGER DEFAULT 5,
                    cd_kef INTEGER DEFAULT 5,
                    cd_all_updates INTEGER DEFAULT 5,
                    cd_last_update INTEGER DEFAULT 5,
                    cd_top INTEGER DEFAULT 5,
                    cd_hey INTEGER DEFAULT 5,
                    cd_raids INTEGER DEFAULT 5
                )
            ''')

            cursor.execute('SELECT * FROM chats WHERE chat_id = ?', (chat_id,))
            existing_chat = cursor.fetchone()

            if not existing_chat:
                cursor.execute('''
                    INSERT INTO chats (
                        chat_id, chat_name, creator_id, creator_username, admin_ids, admin_usernames
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (chat_id, chat_name, creator_id, creator_username, admin_ids, admin_usernames))
                conn.commit()
                print(f"Добавлен новый чат: {chat_id}")
                debug_message(message, f"Добавлен новый чат: {chat_id}")

                cursor.execute('''
                    INSERT INTO access_to_commands (
                        chat_id, chat_name
                    ) VALUES (?, ?)
                ''', (chat_id, chat_name))
                conn.commit()

                cursor.execute('''
                    INSERT INTO command_cooldowns (
                        chat_id, chat_name
                    ) VALUES (?, ?)
                ''', (chat_id, chat_name))
                conn.commit()

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_admins (
                        chat_id INTEGER,
                        admin_id INTEGER,
                        admin_username TEXT,
                        PRIMARY KEY (chat_id, admin_id)
                    )
                ''')

                for admin in admins:
                    cursor.execute('''
                        INSERT INTO chat_admins (chat_id, admin_id, admin_username)
                        VALUES (?, ?, ?)
                    ''', (chat_id, admin.user.id, admin.user.username))
                conn.commit()
            else:
                print(f"Чат уже существует: {chat_id}")

                cursor.execute('SELECT admin_id FROM chat_admins WHERE chat_id = ?', (chat_id,))
                existing_admin_ids = [row[0] for row in cursor.fetchall()]

                current_admin_ids = [admin.user.id for admin in admins]

                if set(existing_admin_ids) != set(current_admin_ids):
                    cursor.execute('DELETE FROM chat_admins WHERE chat_id = ?', (chat_id,))
                    for admin in admins:
                        cursor.execute('''
                            INSERT INTO chat_admins (chat_id, admin_id, admin_username)
                            VALUES (?, ?, ?)
                        ''', (chat_id, admin.user.id, admin.user.username))
                    conn.commit()
                    print(f"Обновлен список администраторов для чата: {chat_id}")

"""



# Функция для проверки санкций
def check_user_sanctions(user_id, message):
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Запрос для получения значения sanctions для данного пользователя
        cursor.execute("SELECT sanctions FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        # Если результат найден и sanctions = Да
        if result and result[0] == "Да":
            debug_message(message, f'{user_id}- Применены санкции, команда не отправлена')
            print("Применены санкции, команда не отправлена!")
            return True  # Пользователь заблокирован
        

        return False  # Пользователь не заблокирован


    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return False
    finally:
        conn.close()






#######################                     ОБЩИЕ (без ограничений где-либо и как-либо)                      ############################


@bot.message_handler(commands=['start', 'старт'])
def start(message):
    handle_message(message)

    path_file = INFO_FOLDER  + "start.txt"

    with open(path_file, 'r', encoding='utf-8') as file:
        start_text = file.read()

    bot.send_message(message.chat.id, start_text)

    debug_message(message, 'Пользователь использовал /start')
    print("Пользователь использовал /start")




"""
@bot.message_handler(commands=['с_команды', 's_commands'])
def command_list(message):
    handle_message(message)
    
    chat_id = message.chat.id

    if message.chat.type not in ('group', 'supergroup'):
        bot.reply_to(message, "Команда /s_commands может использоваться только в групповых чатах!")
        debug_message(message, "Команда /s_commands использована НЕ в групповом чате!")
        return
    
    with sqlite3.connect('chat_servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM access_to_commands WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        
        if result:
            commands_status = {
                "code": result[2],
                "codes": result[3],
                "info": result[4],
                "kef": result[5],
                "raids": result[6],
                "update":result[7],
                "last_update": result[8],
                "all_updates": result[9],
                "thank_you": result[10],
                "coin": result[11],
                "top": result[12],
                "admin": result[13],
                "developer": result[14],
                "upload_photo": result[15],
                "photo": result[16],
                "video": result[17],
                "hey": result[18]
            }

            cursor.execute('SELECT * FROM command_cooldowns WHERE chat_id = ?', (chat_id,))
            cooldowns_result = cursor.fetchone()
            cooldowns = {
                "code": cooldowns_result[1],
                "codes": cooldowns_result[2],
                "info": cooldowns_result[3],
                "kef": cooldowns_result[4],
                "raids": cooldowns_result[5],
                "update":cooldowns_result[6],
                "last_update": cooldowns_result[7],
                "all_updates": cooldowns_result[8],
                "thank_you": cooldowns_result[9],
                "coin": cooldowns_result[10],
                "top": cooldowns_result[11],
                "admin": cooldowns_result[12],
                "developer": cooldowns_result[13],
                "upload_photo": cooldowns_result[14],
                "photo": cooldowns_result[15],
                "video": cooldowns_result[16],
                "hey": cooldowns_result[17]
            }
            
            message_text = "Статус команд на этом сервере:\n"
            for command, status in commands_status.items():
                cooldown_duration = cooldowns.get(command, 5)  # Значение КД по умолчанию 5 секунд
                status_text = "✔️" if status else "❌"
                message_text += f"{status_text}:   /{command} (КД: {cooldown_duration} секунд)\n"

            bot.reply_to(message, message_text)
            debug_message(message, f"Показан список команд на сервере {chat_id}")
        else:
            bot.reply_to(message, "Не удалось получить список команд для этого чата. Сообщите: @DanlokPlay")
            debug_message(message, "Не удалось получить список команд для этого чата.")
    
    print(f"Показан список команд для чата {chat_id}.")


"""












#######################                        Личные без ограничений. В группах возможны ограничения.                        #########################

@bot.message_handler(commands=['спасибо', 'thank_you'])
def thank_you(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 



    """command_name = 'thank_you'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    bot.send_message(chat_id, "Тебе спасибо ^_^\n Теперь разработчик знает, что не зря время тратил :D")
    debug_message(message, 'Спасибо от ')





@bot.message_handler(commands=['info', 'инфо'])
def custom_commands(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'info'

    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере!")
            return
        if not cool_down(message, command_name):
            return
    """
    path_file = INFO_FOLDER + "info.txt"

    with open(path_file, 'r', encoding='utf-8') as file:
        info_custom_text = file.read()

    bot.send_message(chat_id, info_custom_text, reply_to_message_id=message.id)
    
    debug_message(message, 'Команды пользователей высланы')
    print("Информация о пользовательских командах выслана!")



"""
@bot.message_handler(commands=['admin', 'админ'])
def admin_commands(message):
    handle_message(message)

    chat_id = message.chat.id
    command_name = 'admin'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
        
    path_file = INFO_FOLDER + command_name + ".txt"
        
    with open(path_file, 'r', encoding='utf-8') as file:
        info_admin_text = file.read()

    bot.send_message(message.chat.id, info_admin_text, reply_to_message_id=message.id)
    
    debug_message(message, 'Команды админов высланы')
    print("Информация о админских командах выслана!")
"""


@bot.message_handler(commands=['developer', 'разработчик'])
def developer_commands(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'developer'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    path_file = INFO_FOLDER + "developer.txt"
    
    with open(path_file, 'r', encoding='utf-8') as file:
        info_developer_text = file.read()

    bot.send_message(chat_id, info_developer_text, reply_to_message_id=message.id)

    debug_message(message, 'Команды разработчика высланы')
    print("Информация о командах разработчика выслана!")



@bot.message_handler(commands=['код', 'к', 'пароль', 'k', 'kod', 'code', 'password'])
def start_code(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    
    
    """command_name = 'code'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
"""
    text = 'Код на сегодня выслан'
    codes = read_codes_from_file('codes.txt')  # Загружаем коды каждый раз при вызове команды
    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_day = current_datetime.day
    current_year = current_datetime.year
    daily_code = None

    if (current_year, current_month) in codes:
        day_codes = codes[(current_year, current_month)]
        if current_day in day_codes:
            daily_code = day_codes[current_day]
            bot.send_message(chat_id, f"Текущий код:\n{daily_code}\nКоды на месяц: /codes")
        else:
            bot.send_message(chat_id, "Код на сегодня не найден.")
            text = 'Код на сегодня не найдены'
    else:
        bot.send_message(chat_id, "Коды на этот месяц не найдены.")
        text = 'Коды на месяц не найдены'
    debug_message(message, text)

    print("Пароль на сегодня выслан!", current_day, ':', daily_code)

def read_codes_from_file(filename):
    codes = {}
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                try:
                    year_month, codes_str = line.strip().split('::')
                    year, month = map(int, year_month.split('_'))
                    
                    day_codes = {}
                    for day_code in codes_str.split(','):
                        day, code = day_code.split(':')
                        day_codes[int(day)] = code
                    codes[(year, month)] = day_codes
                except ValueError:
                    print(f"Неправильный формат данных в строке: {line.strip()}")
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    return codes



@bot.message_handler(commands=['коды', 'коды_на_месяц', 'месяц', 'бункер', 'бункер_альфа', 'codes'])
def start_codes(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'codes'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
        """
    
    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_year = current_datetime.year

    # Словарь для соответствия месяцев и их названий
    month_names = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь'
    }

    month_name = month_names.get(current_month)
    if month_name:
        filename = f'коды/{month_name} {current_year}.png'
        with open(filename, 'rb') as file:
            bot.send_photo(chat_id, file, f'Коды на {month_name} {current_year}')
        print("Коды на месяцы высланы!")
        debug_message(message, 'Коды на месяц высланы')
    else:
        print("Ошибка: Неверный номер месяца!")



@bot.message_handler(commands=['м', 'монета', 'coin'])
def start_coins(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'coin'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    var = randint(0, 1)
    heads = 'Орёл'
    tails = 'Решка'
    if var == 0:
        bot.send_message(chat_id, f'{heads}', reply_to_message_id=message.id)

        print(f"Подброс монеты сработал! ({heads})")
        debug_message(message, 'Монета подброшена (Орёл):')
        
    else:
        bot.send_message(chat_id, f'{tails}', reply_to_message_id=message.id)

        print(f"Подброс монеты сработал! ({tails})")
        debug_message(message, 'Монета подброшена (Решка):')





@bot.message_handler(commands=['загрузить_фото', 'upload_photo'])
def upload_photo(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    
    
    """command_name = 'upload_photo'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    try:
        photo = message.reply_to_message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        file = bot.download_file(file_info.file_path)
        photo_name = message.text.split(maxsplit=1)[1].strip()

        photo_name = capitalize_photo_name(photo_name)

        if os.path.exists(os.path.join(CHECK_FOLDER, f'{photo_name}.png')):
            bot.reply_to(message, f"Фотография с названием '{photo_name}' уже существует в папке проверки. Пожалуйста, укажите другое имя.")
            debug_message(message, f"Фотография с названием '{photo_name}' уже существует в папке проверки:")
            return

        file_name = os.path.join(CHECK_FOLDER, f'{photo_name}.png')

        with open(file_name, 'wb') as new_file:
            new_file.write(file)

        user_id = message.from_user.id
        user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

        bot.send_message(chat_id, "Фотография успешно загружена. Ожидайте проверки.")
        bot.send_photo(DEVELOPER_ID, file, caption=f"Новая фотография: {photo_name} (Загрузил: {user_name})", reply_markup=approve_keyboard(photo_name, user_id))
        debug_message(message, f"Новая фотография: {photo_name} (Загрузил: {user_name})")

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при загрузке фотографии: {e}. Пожалуйста, попробуйте загрузить фото ещё раз.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_photo'))
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_photo'))
def approve_photo(call):
    photo_name = call.data.split('_')[2]
    user_id = int(call.data.split('_')[3])
    message = call.message

    chat_id = message.chat.id
    message_id = message.message_id

    try:
        if message.reply_markup:
            if call.data.endswith('yes'):
                bot.send_message(message.chat.id, f"Укажите путь, куда переместить фотографию.")
                bot.register_next_step_handler(message, move_photo, photo_name, user_id, chat_id, message_id)
            else:
                # Запрос причины отклонения
                bot.send_message(call.message.chat.id, f"Пожалуйста, укажите причину отклонения фотографии {photo_name}.")
                bot.register_next_step_handler(call.message, ask_rejection_reason, photo_name, user_id, chat_id, message_id)
        else:
            bot.send_message(message.chat.id, "Сообщение уже изменено.")
    except OSError as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла неожиданная ошибка: {e}")

def ask_rejection_reason(message, photo_name, user_id, chat_id, message_id):
    reason = message.text.strip()

    try:
        # Удаляем фотографию
        os.remove(os.path.join(CHECK_FOLDER, f'{photo_name}.png'))

        # Сообщаем пользователю об отклонении и причине
        bot.send_message(user_id, f"Ваша фотография {photo_name} была отклонена. Причина: {reason}")
        
        # Отправляем причину в исходный чат
        bot.send_message(chat_id, f"Фотография {photo_name} отклонена. Причина: {reason}")

        # Убираем кнопки с сообщения
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке отклонения фотографии: {e}")

def move_photo(message, photo_name, user_id, chat_id, message_id):
    try:
        destination_path = message.text.strip()
        if not os.path.exists(destination_path):
            bot.send_message(message.chat.id, f"Указанный путь '{destination_path}' не существует. Хотите его создать? (да/нет)")
            bot.register_next_step_handler(message, confirm_create_directory, photo_name, user_id, chat_id, message_id, destination_path)
            return

        if os.path.abspath(destination_path) == os.path.abspath(CHECK_FOLDER):
            bot.send_message(message.chat.id, "Нельзя перемещать в эту папку.")
            debug_message(message, f"Нельзя перемещать в эту папку check/:")
            return

        move_photo_to_destination(photo_name, user_id, chat_id, message_id, destination_path)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

def confirm_create_directory(message, photo_name, user_id, chat_id, message_id, destination_path):
    try:
        if message.text.strip().lower() in ['да', 'yes']:
            os.makedirs(destination_path)
            bot.send_message(message.chat.id, f"Путь '{destination_path}' создан.")
            move_photo_to_destination(photo_name, user_id, chat_id, message_id, destination_path)
        else:
            bot.send_message(message.chat.id, "Перемещение отменено.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при создании директории: {e}")

def move_photo_to_destination(photo_name, user_id, chat_id, message_id, destination_path):
    try:
        source = os.path.join(CHECK_FOLDER, f'{photo_name}.png')
        destination = os.path.join(destination_path, f'{photo_name}.png')

        if os.path.exists(destination):
            bot.send_message(chat_id, f"Файл с названием '{photo_name}' уже существует в целевой папке. Укажите другой путь.")
            debug_message(chat_id, f"Файл с названием '{photo_name}' уже существует в целевой папке:")
            return

        os.rename(source, destination)
        bot.send_message(chat_id, f"Фотография {photo_name} перемещена по указанному пути.")

        bot.send_message(user_id, f"Фотография {photo_name} одобрена!")
        increase_survival_points(user_id)

        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)

        bot.send_message(DEVELOPER_ID, 'Изменить файл с путями: /rewrite')
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка при перемещении фотографии: {e}")

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return None

def rewrite_file(file_path, new_content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)

def capitalize_photo_name(photo_name):
    return photo_name.capitalize()

def increase_survival_points(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET survival_points = survival_points + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def approve_keyboard(photo_name, user_id):
    keyboard = types.InlineKeyboardMarkup()
    approve_button = types.InlineKeyboardButton(text="Одобрить", callback_data=f"approve_photo_{photo_name}_{user_id}_yes")
    reject_button = types.InlineKeyboardButton(text="Отклонить", callback_data=f"approve_photo_{photo_name}_{user_id}_no")
    keyboard.row(approve_button, reject_button)
    return keyboard



@bot.message_handler(commands=['фото', 'ф', 'photo', 'ph'])
def choice (message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    """command_name = 'photo'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    send_photo_by_name_pc(message)

def find_photo_in_folders(photo_name, folder):
    found_files = []

    # Игнорируем папку "check"
    if folder.endswith("check"):
        return found_files

    # Ищем файлы с заданным именем в текущей папке
    search_pattern = os.path.join(folder, f"*{photo_name}.png")
    found_files += glob.glob(search_pattern)

    # Перебираем подпапки и ищем в них
    subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]
    for subfolder in subfolders:
        found_files += find_photo_in_folders(photo_name, subfolder)

    return found_files


def send_photo_by_name_pc(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Вы не указали название фото.\n Примеры: /ф глок, /ф доставки")
        debug_message(message, f"Не указано название фото:")
        return

    try:
        photo_name = message.text.split(maxsplit=1)[1].capitalize()  # Название фото
        
        # Создаем список папок, в которых нужно искать фотографии
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folders = [folder for folder in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, folder))]

        found_files = []  # инициализируем переменную found_files здесь

        # Перебираем папки и ищем файлы в них
        for folder in folders:
            found_files += find_photo_in_folders(photo_name, folder)

        if not found_files:
            raise FileNotFoundError

        # Отправляем фото пользователю
        for found_file in found_files:
            with open(found_file, 'rb') as photo_file:
                bot.send_photo(message.chat.id, photo_file, f'{photo_name}')

        # Отправляем уведомление
        print('Фото отослано!')
        debug_message(message, f'Фото {photo_name} было просмотрено')

    except FileNotFoundError:
        bot.reply_to(message, f"Фотография с названием '{photo_name}' не найдена.\nДля просмотра доступных фото напишите команду /кеф\n Примеры: /ф глок, /ф доставки")
        debug_message(message, f'Нет фотографии с названием {photo_name}')
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")



@bot.message_handler(commands=['видео', 'video', 'в', 'v'])
def handle_videos_command(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'video'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    try:
        with open('videos.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            bot.send_message(chat_id, f"{content}")
    except FileNotFoundError:
        bot.reply_to(message, "Файл videos.txt не найден.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")



@bot.message_handler(commands=['пр_фото', 'пример_фото', 'пр_ф', 'пф', 'кеф', 'kef'])
def list_photos_commads(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'kef'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
        """
    try:
        # Читаем содержимое файла с названиями фотографий
        with open('photos.txt', 'r', encoding='utf-8') as txt_file:
            photo_names = txt_file.readlines()

        # Проверяем, есть ли хотя бы одно название фотографии
        if photo_names:
            # Формируем строку с названиями фотографий
            photo_names_string = "".join(photo_names)
            # Отправляем названия фотографий в чат одним сообщением
            bot.send_message(message.chat.id, f"\n{photo_names_string}")
        else:
            bot.reply_to(message, "Нет загруженных фотографий.")

        print('Список названий фотографий отослан!')
        debug_message(message, 'Просмотрен список фотографий')

    except FileNotFoundError:
        bot.reply_to(message, "Файл с названиями фотографий не найден.")
        debug_message(message, 'Файл с названиями фотографий не найден')
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при отправке названий фотографий: {e}")
        debug_message(message, f"Произошла ошибка при отправке названий фотографий: {e}")



@bot.message_handler(commands=['обновления_бота', 'bot_updates'])
def bot_updates(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'bot_updates'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
        """
    path_file = INFO_FOLDER + "bot_updates.txt"
    
    with open(path_file, 'rb') as updates_file:
        bot.send_document(chat_id, updates_file)
            
    debug_message(message, 'Просмотрены ВСЕ обновления')
    print('Обновления Бота отосланы!')



@bot.message_handler(commands=['последнее_обновление_бота', 'last_bot_update'])
def last_updates(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'last_update'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
        """
    path_file = INFO_FOLDER + "last_bot_update.txt"
    path_photo = INFO_FOLDER + "last_bot_update.png"
    
    with open(path_file, 'r', encoding='utf-8') as updates_file:
        updates_text = updates_file.read()
    
    with open(path_photo, 'rb') as photo_file:
        bot.send_photo(chat_id, photo_file, caption=updates_text)
            
    debug_message(message, 'Просмотрено последнее обновление')
    print('Последнее обновление Бота отослано!')




@bot.message_handler(commands=['топ', 'top'])
def top_users(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Выбираем всех пользователей, у которых количество очков больше 0
    cursor.execute("SELECT id, username, name, surname, survival_points FROM users WHERE survival_points > 0")

    # Получаем результаты запроса
    users = cursor.fetchall()

    # Сортируем пользователей по количеству очков в убывающем порядке
    sorted_users = sorted(users, key=lambda x: x[4], reverse=True)

    # Формируем сообщение с топом пользователей
    top_message = "🏆 Топ пользователей, которые заполнили бота информацией🏆\n\n"
    for index, user in enumerate(sorted_users, start=1):
        user_info = f"{index}. "
        if user[1]:  # Если у пользователя есть username
            user_info += f"@{user[1]}"
        else:  # Иначе выводим имя и фамилию
            user_info += f"{user[2]} {user[3]}"
        user_info += f" - {user[4]} очков\n"
        top_message += user_info

    # Отправляем сообщение с топом пользователей
    bot.send_message(chat_id, top_message)
    debug_message(message, f"Топ пользователей отосланы по загрузке фото:")

    conn.close()


"""
# Список с тремя различными смайликами
smileys = ["💩", "🎁", "☣️"]

@bot.message_handler(commands=['рулетка', 'roulette', 'r', 'р'])
def roulette(message):
    handle_message(message)

    chat_id = message.chat.id
    command_name = 'roulette'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    
    # Генерируем три случайных смайлика с повторениями
    random_smileys = [random.choice(smileys) for _ in range(3)]
    
    # Формируем строку из трех случайно выбранных смайликов
    result = " ".join(random_smileys)
    
    # Отправляем смайлики в чат
    bot.send_message(message.chat.id, result, reply_to_message_id=message.id)

    print('Рулетка сработала!')
    debug_message(message, f'Рулетка сработала!({result})')
"""

# Функция для чтения случайной строки из файла
def get_random_phrase():
    with open(INFO_FOLDER + 'phrases.txt', 'r', encoding='utf-8') as file:
        phrases = file.readlines()
    return random.choice(phrases).strip()

@bot.message_handler(commands=['эй', 'hey'])
def send_random_phrase(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'hey'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    phrase = get_random_phrase()
    bot.send_message(chat_id, phrase)

    print('Запрошена случайная фраза') 
    debug_message(message, f'Запрошена случайная фраза')



@bot.message_handler(commands=['рейды', 'raids'])
def send_apk(message):
    handle_message(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return 
    

    """command_name = 'raids'
    
    if message.chat.type != 'private':
        if not check_access(chat_id, command_name):
            bot.reply_to(message, "Эта команда отключена на этом сервере.")
            return
        if not cool_down(message, command_name):
            return
    """
    try:
        bot.send_message(
            chat_id,
            "Скачать Базы LDoE \n\n"
            "AppGallery (Android 6.0):\n https://appgallery.huawei.ru/app/C111738085\n"
            "RuStore (Android 6.0):\n https://www.rustore.ru/catalog/app/com.DanlokPlay.LDoEBases\n\n"
            "Скачать Базы LDoE \n"
            "Сайт (с Android 5.1):\n https://ldoe.danlokplay.ru/Bases\n\n"
            "Чат по игре: https://t.me/LastSurvivorsLDoE\n"
        )
        debug_message(message, 'Отправлены ссылки на Базы LDoE')
        print('Отправлены ссылки на Базы LDoE')
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")



def get_current_version():
    with open(INFORMATION_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return int(data.get("versionUpdate"))

def find_latest_version(version):
    while True:
        url = f"{BASE_URL}p{version + 1}.json.gz"
        response = requests.head(url)
        if response.status_code == 200:
            version += 1
        else:
            break
    return version

def download_and_extract_file(version):
    # Формируем имена для файлов
    compressed_file_name = os.path.join(UPDATE_FOLDER, f"p{version}.json.gz")
    uncompressed_file_name = os.path.join(UPDATE_FOLDER, f"p{version}.json")

    # Проверяем, существует ли уже файл
    if os.path.exists(compressed_file_name):
        print(f"Файл p{version} уже существует. Скачивание пропущено.")
        # Если файл уже существует, распаковываем его заново
        return extract_json_from_file(compressed_file_name, uncompressed_file_name)

    # Если файла нет, скачиваем его
    url = f"{BASE_URL}p{version}.json.gz"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Файл p{version} найден и загружен.")
        
        # Сохраняем сжатый файл
        os.makedirs(UPDATE_FOLDER, exist_ok=True)
        with open(compressed_file_name, "wb") as f:
            f.write(response.content)

        # Распаковываем архив
        return extract_json_from_file(compressed_file_name, uncompressed_file_name)

    print(f"Файл p{version} недоступен.")
    return None

def extract_json_from_file(compressed_file_name, uncompressed_file_name):
    # Распаковка архива
    with gzip.open(compressed_file_name, "rb") as gz:
        with open(uncompressed_file_name, "wb") as json_file:
            json_file.write(gz.read())

    # Чтение распакованного JSON
    with open(uncompressed_file_name, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Файл {uncompressed_file_name} обработан.")
    return data

def update_version_in_file(new_version):
    # Обновляем версию в INFORMATION_FILE
    try:
        with open(INFORMATION_FILE, 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data["versionUpdate"] = new_version  # Обновляем версию
            file.seek(0)  # Возвращаемся в начало файла
            json.dump(data, file, ensure_ascii=False, indent=4)  # Перезаписываем файл
            file.truncate()  # Обрезаем файл до текущего размера
        print(f"Файл {INFORMATION_FILE} обновлен до версии {new_version}")
    except Exception as e:
        print(f"Не удалось обновить файл {INFORMATION_FILE}: {e}")

def send_update_message(chat_id, json_data):
    if json_data:
        russian_text = json_data.get("Russian", "Нет данных")
        english_text = json_data.get("English", "No data")
        message = f"<b> Последнее найденное ОБНОВЛЕНИЕ:</b>\n\n🇷🇺 {russian_text}\n\n🇺🇸 {english_text}"
        bot.send_message(chat_id, message, parse_mode="HTML")

# Обработчик команды /update
@bot.message_handler(commands=['update', 'обновление'])
def handle_update_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Не-а")
        return
    
    try:
        version = get_current_version()  # Получаем текущую версию
        new_version = find_latest_version(version)  # Находим последнюю доступную версию

        # Если новая версия отличается от текущей
        if new_version > version:
            json_data = download_and_extract_file(new_version)  # Загружаем и распаковываем файл

            if json_data:
                send_update_message(chat_id, json_data)  # Отправляем обновления пользователю
                update_version_in_file(new_version)  # Обновляем версию в файле только после успешного скачивания
                debug_message(message, 'Отправлено последнее найденное обновление на сервере по LDoE')
                print('Отправлено последнее найденное обновление на сервере по LDoE')
            else:
                bot.reply_to(message, "Не удалось загрузить обновление.")
                print("Не удалось загрузить обновление.")
        else:
            # Если новая версия не найдена, отправляем последнее доступное обновление
            json_data = download_and_extract_file(version)  # Отправляем текущее обновление
            if json_data:
                send_update_message(chat_id, json_data)  # Отправляем текущее обновление пользователю
                debug_message(message, 'Отправлено текущее доступное обновление.')
                print('Отправлено текущее доступное обновление.')
            else:
                bot.reply_to(message, "Не удалось загрузить обновление.")
                print("Не удалось загрузить обновление.")

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
















####################                   АДМИНЫ (В группах) + создатель                       ###########################

"""
@bot.message_handler(commands=['изменить_кд', 'change_cd', 'change_cooldown'])
def change_cooldown(message):
    handle_message(message)
    
    if message.chat.type not in ('group', 'supergroup'):
        bot.reply_to(message, "Команда /изменить_кд может использоваться только в групповых чатах!")
        debug_message(message, "Команда /изменить_кд может использоваться только в групповых чатах")
        return
    
    chat_id = message.chat.id
    
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID and not is_chat_admin(bot, chat_id, user_id):
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды")
        debug_message(message, "Попытка изменить КД у чата без достаточных прав")
        return
    
    try:
        command, new_cooldown = message.text.split()[1:3]
        new_cooldown = int(new_cooldown)
    except (IndexError, ValueError):
        bot.reply_to(message, "Используйте команду в формате: /изменить_кд <команда> <сек>")
        debug_message(message, "Используйте команду в формате: /изменить_кд <команда> <сек>")
        return
    
    if not (0 <= new_cooldown <= 1_000_000):
        bot.reply_to(message, "Новое значение КД должно быть целым числом от 0 до 1 000 000 секунд")
        debug_message(message, "Новое значение КД должно быть целым числом от 0 до 1 000 000 секунд")
        return

    command_column = f'cd_{command}'
    
    with sqlite3.connect('chat_servers.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(command_cooldowns)")
        columns = [description[1] for description in cursor.fetchall()]
        if command_column not in columns:
            bot.reply_to(message, f"Команда '{command}' не найдена!")
            debug_message(message, f"Команда '{command}' не найдена")
            return
        
        cursor.execute(f'''
            UPDATE command_cooldowns
            SET {command_column} = ?
            WHERE chat_id = ?
        ''', (new_cooldown, chat_id))
        conn.commit()

        if cursor.rowcount > 0:
            bot.reply_to(message, f"Значение КД для команды '{command}' успешно изменено на {new_cooldown} секунд")
            debug_message(message, f"Значение КД для команды '{command}' успешно изменено на {new_cooldown} секунд")
        else:
            bot.reply_to(message, "Ошибка при изменении значения КД")
            debug_message(message, "Ошибка при изменении значения КД")



@bot.message_handler(commands=['изменить_доступ', 'change_access'])
def change_access(message):
    handle_message(message)
    
    if message.chat.type not in ('group', 'supergroup'):
        bot.reply_to(message, "Команда /изменить_доступ может использоваться только в групповых чатах!")
        debug_message(message, "Команда /изменить_доступ может использоваться только в групповых чатах!")
        return
    
    chat_id = message.chat.id
    
    user_id = message.from_user.id
    if user_id != DEVELOPER_ID and not is_chat_admin(bot, chat_id, user_id):
        bot.reply_to(message, "У вас недостаточно прав для выполнения этой команды!")
        debug_message(message, "Попытка изменить доступ к команде в чате без достаточных прав!")
        return
    
    try:
        command_name, access_value = message.text.split()[1:3]
        access_value = int(access_value)
        if access_value not in (0, 1):
            raise ValueError("Значение должно быть 0 или 1")
    except (ValueError, IndexError):
        bot.reply_to(message, "Используйте команду в формате: /изменить_доступ <команда> <0 или 1>")
        debug_message(message, "Используйте команду в формате: /изменить_доступ <команда> <0 или 1>")
        return

    with sqlite3.connect('chat_servers.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(access_to_commands)")
        columns = [description[1] for description in cursor.fetchall()]
        if command_name not in columns:
            bot.reply_to(message, f"Команда '{command_name}' не найдена")
            debug_message(message, f"Команда '{command_name}' не найдена")
            return
        
        cursor.execute(f'UPDATE access_to_commands SET {command_name} = ? WHERE chat_id = ?', (access_value, chat_id))
        conn.commit()
        
        bot.reply_to(message, f"Доступ к команде '{command_name}' был успешно {'включен' if access_value == 1 else 'отключен'}")
        debug_message(message, f"Доступ к команде '{command_name}' был успешно {'включен' if access_value == 1 else 'отключен'}")

"""















##################                Только РАЗРАБОТЧИКА                #####################

# Сначала записать коды, потом с упоминанием этого сообщения выполнить команду
@bot.message_handler(commands=['записать_коды'])
def write_codes(message):
    handle_message(message)
    # Проверяем, что пользователь, вызвавший команду, является администратором
    if message.from_user.id != DEVELOPER_ID:
        bot.reply_to(message, "Извините, у вас нет прав на выполнение этой команды.")
        debug_message(message, 'Попытался записать коды:')
        return

    # Проверяем, что в сообщении, содержащем команду, есть данные для записи
    if not message.reply_to_message or not message.reply_to_message.text:
        bot.reply_to(message, "Не найдено сообщение для записи в файл.")
        debug_message(message, 'Не найдено сообщение для записи в файл кодов: ')
        return

    # Получаем текст сообщения, на которое был отправлен ответ, и добавляем символ новой строки
    try:
        codes_text = message.reply_to_message.text.strip()
        year_month, codes = codes_text.split('\n', 1)  # Разделяем год_месяц и коды
        codes = codes.replace('\n', ',')  # Заменяем символы новой строки на запятые
        codes_text = '\n' + f'{year_month}::{codes}'  # Форматируем строку с кодами

        # Записываем полученные коды в файл
        filename = 'codes.txt'
        with open(filename, 'a') as file:
            file.write(codes_text)
        bot.reply_to(message, "Коды успешно записаны в файл.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при записи кодов в файл: {e}")

    print('Коды записаны!')
    debug_message(message, 'Коды были записаны в файл:')




@bot.message_handler(commands=['перезаписать', 'rewrite'])
def handle_rewrite_command(message):
    handle_message(message)
    try:
        if message.from_user.id != DEVELOPER_ID:
            bot.reply_to(message, "У вас нет прав для использования этой команды.")
            debug_message(message, f"Попытался использовать команду /перезаписать")
            return

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Photos", callback_data="rewrite_photos"))
        keyboard.add(types.InlineKeyboardButton(text="Videos", callback_data="rewrite_videos"))
        keyboard.add(types.InlineKeyboardButton(text="Logs Times", callback_data="rewrite_log_times"))
        
        bot.send_message(message.chat.id, "Выберите файл для перезаписи:", reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('rewrite_'))
def handle_rewrite_callback(call):
    try:
        if call.from_user.id != DEVELOPER_ID:
            bot.answer_callback_query(call.id, "У вас нет прав для использования этой команды.")
            debug_message(call.message, f"Попытался использовать команду /перезаписать")
            return

        if call.data == 'rewrite_photos':
            file_path = 'photos.txt'
        elif call.data == 'rewrite_videos':
            file_path = 'videos.txt'
        elif call.data == 'rewrite_log_times':
            file_path = 'information.json'  # Обрабатываем JSON файл
        else:
            bot.answer_callback_query(call.id, "Неверный выбор.")
            debug_message(call.message, f"Неверный выбор файла для его перезаписи")
            return

        current_content = None

        if file_path == 'information.json':
            # Для логов получаем текущие данные из JSON
            current_content = read_log_times()
            if not current_content:
                current_content = "Файл пуст или логи не найдены."
        else:
            current_content = read_file_content(file_path)

        if current_content is None:
            bot.send_message(call.message.chat.id, f"Файл {file_path} не найден.")
            debug_message(call.message, f"Файла для перезаписи содержимого не найден")
            return

        # Отправка текущего содержимого файла пользователю
        bot.send_message(call.message.chat.id, f"{file_path}:\n\n{current_content}")
        
        # Запрос нового содержимого у пользователя
        bot.send_message(call.message.chat.id, f"Отправьте новое содержимое для файла {file_path}.")
        bot.register_next_step_handler(call.message, process_new_content, file_path)
    
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Произошла ошибка: {e}")

def process_new_content(message, file_path):
    try:
        new_content = message.text.strip()

        if file_path == 'information.json':
            # Для log_times нужно обработать JSON
            new_log_times = [time.strip() for time in new_content.split(',') if time.strip()]

            valid_times = []
            time_pattern = re.compile(r"^\d{2}:\d{2}(:\d{2})?$")

            for time in new_log_times:
                if time_pattern.match(time):
                    valid_times.append(time)
                else:
                    bot.send_message(message.chat.id, f"Неверный формат времени: {time}. Ожидается формат HH:MM или HH:MM:SS.")

            if valid_times:
                # Перезапись данных в JSON файл
                write_log_times(valid_times)
                bot.reply_to(message, f"Время логов успешно перезаписано: {', '.join(valid_times)}")
            else:
                bot.reply_to(message, "Не удалось сохранить корректное время. Попробуйте снова.")
        
        else:
            # Для photos.txt и videos.txt обычная перезапись
            rewrite_file(file_path, new_content)
            bot.reply_to(message, f"Файл {file_path} успешно перезаписан.")

        debug_message(message, f"Файл {file_path} успешно перезаписан")

        # Перепланировать задачи, если файл log_times.txt был перезаписан
        if file_path == 'information.json':
            schedule_log_sending()
            bot.send_message(message.chat.id, "Расписание отправки логов обновлено.")
    
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при перезаписи файла: {e}")

def write_log_times(log_times):
    """Перезапись времени логов в JSON файл."""
    try:
        data = {"log_times": log_times}
        with open("information.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        bot.send_message(DEVELOPER_ID, "Время логов успешно обновлено.")
    except Exception as e:
        bot.send_message(DEVELOPER_ID, f"Ошибка при записи времени логов в файл: {e}")



@bot.message_handler(commands=['кд_лог', 'cd_log'])
def send_log_times(message):
    handle_message(message)
    
    # Проверка прав доступа
    if message.from_user.id != DEVELOPER_ID:
        bot.reply_to(message, "У вас нет прав для использования этой команды.")
        return

    try:
        log_times = read_log_times()  # Чтение времени из файла
        if log_times:
            formatted_times = '\n'.join(log_times)  # Форматирование времени для отправки
            bot.reply_to(message, f"Время отправки логов:\n{formatted_times}")
        else:
            bot.reply_to(message, "Нет времени для отправки логов или файл пуст.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при чтении времени логов: {e}")



def send_logs():
    try:
        if os.path.exists(TEMP_LOG_FILE):
            if os.path.getsize(TEMP_LOG_FILE) > 0:
                with open(TEMP_LOG_FILE, 'rb') as temp_file:
                    bot.send_document(DEVELOPER_ID, temp_file)
                # Очищаем файл после отправки
                with open(TEMP_LOG_FILE, 'w', encoding='utf-8') as temp_file:
                    temp_file.write('')
            else:
                bot.send_message(DEVELOPER_ID, 'Бот работает! Файл temp_logs ПУСТОЙ!')
        else:
            bot.send_message(DEVELOPER_ID, 'Бот работает! Файла temp_logs НЕТ!')
    except Exception as e:
        bot.send_message(DEVELOPER_ID, f'Ошибка при отправке логов: {str(e)}')

def read_log_times():
    """Чтение времени отправки логов из JSON-файла."""
    if os.path.exists("information.json"):
        with open("information.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                log_times = data.get("log_times", [])  # Получаем список времени логов

                # Фильтрация корректных форматов времени
                valid_times = []
                time_pattern = re.compile(r"^\d{2}:\d{2}(:\d{2})?$")
                for time in log_times:
                    if time_pattern.match(time):
                        valid_times.append(time)
                    else:
                        bot.send_message(DEVELOPER_ID, f"Неверный формат времени: {time}. Ожидается формат HH:MM или HH:MM:SS.")
                return valid_times
            except json.JSONDecodeError:
                bot.send_message(DEVELOPER_ID, "Ошибка при чтении JSON файла.")
                return []
    return []

def schedule_log_sending():
    """Запланировать отправку логов на основе времени из файла."""
    schedule.clear()  # Очистить все запланированные задачи

    times = read_log_times()
    if not times:
        bot.send_message(DEVELOPER_ID, 'Нет допустимого времени для отправки логов. Расписание не установлено.')
        return

    for log_time in times:
        schedule.every().day.at(log_time).do(send_logs)

def process_new_content(message, file_path):
    try:
        new_content = message.text.strip()
        
        # Перезапись файла с новым содержимым
        rewrite_file(file_path, new_content)
        
        bot.reply_to(message, f"Файл {file_path} успешно перезаписан.")
        debug_message(message, f"Файл {file_path} успешно перезаписан")

        # Перепланировать задачи, если файл `log_times.txt` был перезаписан
        if file_path == 'log_times.txt':
            schedule_log_sending()
            bot.send_message(message.chat.id, "Расписание отправки логов обновлено.")
    
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при перезаписи файла: {e}")

def rewrite_file(file_path, content):
    """Перезапись файла с новым содержимым."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Запуск планировщика при старте
schedule_log_sending()

# Запуск планировщика в отдельном потоке
def run_scheduler():
    while True:
        schedule.run_pending()

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Отправка логов при запуске бота
send_logs()

while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=20)
    except Exception as e:
        print(f"Ошибка в работе бота: {e}")
        time.sleep(5)  # Ожидание перед перезапуском в случае ошибки