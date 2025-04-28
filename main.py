from config import API_TOKEN, DEVELOPER_ID, LOG_FILE, TEMP_LOG_FILE, CHECK_FOLDER, INFO_FOLDER, UPDATE_FOLDER, CODES_FOLDER, CONFIG_URL
import random

import telebot
from telebot import types

import re
import os

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz

from parce_codes import download_image
from read_codes import process_image

import requests
import gzip
import json

import sqlite3

token = API_TOKEN
bot = telebot.TeleBot(token)
TIMEZONE = pytz.timezone('Europe/Moscow')

# Создаём планировщик задач
scheduler = BackgroundScheduler()

# Регистрация обработчика сообщений
#@bot.message_handler(func=lambda message: message)  (Улавливает каждое сообщение)
# Вызывается при выполнении той или иной команды
def handle_message(message): 
    user_id = message.from_user.id
    username = message.from_user.username or None
    first_name = message.from_user.first_name or None
    last_name = message.from_user.last_name or None
    current_time = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()

        # Проверяем, есть ли пользователь в БД
        cursor.execute('SELECT username, name, surname FROM users WHERE id = ?', (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            old_username, old_name, old_surname = existing_user

            if (username != old_username) or (first_name != old_name) or (last_name != old_surname):
                cursor.execute(''' 
                    UPDATE users 
                    SET username = ?, name = ?, surname = ?, last_time = ? 
                    WHERE id = ?
                ''', (username, first_name, last_name, current_time, user_id))
                print(f"Обновлены данные пользователя: {user_id}")
                debug_message(message, f"Обновлены данные пользователя: {user_id}")
            else:
                cursor.execute('UPDATE users SET last_time = ? WHERE id = ?', (current_time, user_id))
        else:
            cursor.execute(''' 
                INSERT INTO users (id, username, name, surname, last_time) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, current_time))
            print(f"Добавлен новый пользователь: {user_id}")
            debug_message(message, f"Добавлен новый пользователь: {user_id}")

        conn.commit()

########################                    МНОГО ИСПОЛЬЗУЕМЫЕ ФУНКЦИИ                     ###############################

# Добавление/обновление пользователя в БД и проверка его на ОГРАНИЧЕНИЯ
def allow_command(message):
    handle_message(message)

    user_id = message.from_user.id

    if check_user_sanctions(user_id, message):
        bot.reply_to(message, "Что-то не так, можно подправить, если подумать :D")
        return False
    
    return True


# Отправка Log
def debug_message(message, additional_text):
    chat_name = message.chat.title if message.chat.title else message.chat.username
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    notification_text = f'{additional_text} @{username} в чате {chat_name}'
    
    # Получаем текущее время по МСК
    current_time_msk = get_current_time_in_timezone()

    # Отправка сообщения разработчику
    if additional_text == 'Спасибо от ':
        bot.send_message(DEVELOPER_ID, f'Спасибо от @{username}')

    # Запись в лог-файл
    log_entry = f'{current_time_msk} - {notification_text}\n'
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)
    with open(TEMP_LOG_FILE, 'a', encoding='utf-8') as temp_log_file:
        temp_log_file.write(log_entry)


# Проверка САНКЦИЙ
# Некоторым пользователи будут лишены возможности пользоваться ботом (Указываются вручную в БД)
def check_user_sanctions(user_id, message):
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sanctions FROM users WHERE id = ?", (user_id,))
            sanctions = (cursor.fetchone() or [None])[0]  # Если пользователя нет, вернёт None

            if sanctions == "Да":
                debug_message(message, f'{user_id} - Применены санкции, команда не отправлена')
                print("Применены санкции, команда не отправлена!")
                return True  # Пользователь заблокирован
    except sqlite3.Error as e:
        print(f"Ошибка при работе с БД: {e}")

    return False

#######################                     ВПОМОГАТЕЛЬНЫЕ ФУНКЦИИ                      ############################

# Вывод времени в выбранной TIMEZONE
def get_current_time_in_timezone():
    now = datetime.now(TIMEZONE)
    return now.strftime("%Y-%m-%d %H:%M:%S")


# Функция для чтения случайной строки из файла
def get_random_phrase():
    with open(INFO_FOLDER + 'phrases.txt', 'r', encoding='utf-8') as file:
        phrases = file.readlines()
    return random.choice(phrases).strip()


#######################                     Стартовая Команда                      ############################

@bot.message_handler(commands=['start', 'старт'])
def start(message):
    handle_message(message)

    path_file = INFO_FOLDER  + "start.txt"

    with open(path_file, 'r', encoding='utf-8') as file:
        start_text = file.read()

    bot.send_message(message.chat.id, start_text, message.message_thread_id)

    debug_message(message, 'Пользователь использовал /start')
    print("Пользователь использовал /start")


#######################                        Вспомогательные команды                       #########################

@bot.message_handler(commands=['спасибо', 'thank_you'])
def thank_you(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id

    bot.send_message(chat_id, "Тебе спасибо ^_^\n Теперь разработчик знает, что не зря время тратил :D", message_thread_id=thread_id)
    debug_message(message, 'Спасибо от ')
    print(f"Пользователь использовал /start")



@bot.message_handler(commands=['м', 'монета', 'coin'])
def start_coins(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id

    var = random.randint(0, 1)
    heads = 'Орёл'
    tails = 'Решка'
    if var == 0:
        bot.send_message(chat_id, f'{heads}', reply_to_message_id=message.id, message_thread_id=thread_id)

        print(f"Подброс монеты сработал! ({heads})")
        debug_message(message, 'Монета подброшена (Орёл):')
        
    else:
        bot.send_message(chat_id, f'{tails}', reply_to_message_id=message.id, message_thread_id=thread_id)

        print(f"Подброс монеты сработал! ({tails})")
        debug_message(message, 'Монета подброшена (Решка):')


@bot.message_handler(commands=['эй', 'hey'])
def send_random_phrase(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id

    bot.send_message(chat_id, get_random_phrase(), message_thread_id=thread_id)

    print('Запрошена случайная фраза') 
    debug_message(message, f'Запрошена случайная фраза')



#######################                        КОМАНДЫ                       #########################


@bot.message_handler(commands=['info', 'инфо'])
def custom_commands(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    path_file = INFO_FOLDER + "info.txt"

    with open(path_file, 'r', encoding='utf-8') as file:
        info_custom_text = file.read()

    bot.send_message(chat_id, info_custom_text, reply_to_message_id=message.id, message_thread_id=thread_id)
    
    debug_message(message, 'Команды пользователей высланы')
    print("Информация о пользовательских командах выслана!")



@bot.message_handler(commands=['developer', 'разработчик'])
def developer_commands(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    path_file = INFO_FOLDER + "developer.txt"
    
    with open(path_file, 'r', encoding='utf-8') as file:
        info_developer_text = file.read()

    bot.send_message(chat_id, info_developer_text, reply_to_message_id=message.id, message_thread_id=thread_id)

    debug_message(message, 'Команды разработчика высланы')
    print("Информация о командах разработчика выслана!")



@bot.message_handler(commands=['код', 'к', 'пароль', 'k', 'kod', 'code', 'password'])
def start_code(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id

    text = 'Код на сегодня выслан'
    
    # Загружаем коды из сжатого JSON
    filename = 'codes.json.gz'
    try:
        with gzip.open(filename, 'rt', encoding='utf-8') as file:
            codes_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        codes_data = {}

    # Получаем текущую дату
    current_datetime = datetime.now()
    current_year = str(current_datetime.year)
    current_month = f"{current_datetime.month:02d}"  # Делаем двузначным (например, "03")
    current_day = str(current_datetime.day)

    daily_code = None

    # Проверяем, есть ли коды для текущего месяца
    if current_year in codes_data and current_month in codes_data[current_year]:
        day_codes = codes_data[current_year][current_month]
        if current_day in day_codes:
            daily_code = day_codes[current_day]
            bot.send_message(chat_id, f"Текущий код:\n{daily_code}\nКоды на месяц: /codes", message_thread_id=thread_id)
        else:
            bot.send_message(chat_id, "Код на сегодня не найден. Попробуйте: /codes", message_thread_id=thread_id)
            text = 'Код на сегодня не найден'
    else:
        bot.send_message(chat_id, "Коды на этот месяц не найдены. Попробуйте: /codes", message_thread_id=thread_id)
        text = 'Коды на месяц не найдены'

    debug_message(message, text)
    print("Пароль на сегодня выслан!", current_day, ':', daily_code)



@bot.message_handler(commands=['коды', 'коды_на_месяц', 'месяц', 'бункер', 'бункер_альфа', 'codes'])
def start_codes(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_year = current_datetime.year

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
        filename = CODES_FOLDER + f'{month_name} {current_year}.png'
        with open(filename, 'rb') as file:
            bot.send_photo(chat_id, file, f'Коды на {month_name} {current_year}', message_thread_id=thread_id)
        print("Коды на месяцы высланы!")
        debug_message(message, 'Коды на месяц высланы')
    else:
        print("Ошибка: Неверный номер месяца!")



@bot.message_handler(commands=['видео', 'video', 'в', 'v'])
def handle_videos_command(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    try:
        with open('videos.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            bot.send_message(chat_id, f"{content}", message_thread_id=thread_id)
    except FileNotFoundError:
        bot.reply_to(message, "Файл videos.txt не найден.", message_thread_id=thread_id)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")



@bot.message_handler(commands=['пр_фото', 'пример_фото', 'пр_ф', 'пф', 'кеф', 'kef'])
def list_photos_commads(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    with open('photos.txt', 'r', encoding='utf-8') as txt_file:
        photo_names = txt_file.readlines()

    if photo_names:
        photo_names_string = "".join(photo_names)
        bot.send_message(chat_id, f"\n{photo_names_string}", message_thread_id=thread_id)
    else:
        bot.reply_to(message, "Нет загруженных фотографий.")

    print('Список названий фотографий отослан!')
    debug_message(message, 'Просмотрен список фотографий')



@bot.message_handler(commands=['обновления_бота', 'bot_updates'])
def bot_updates(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    path_file = INFO_FOLDER + "bot_updates.txt"
    
    with open(path_file, 'rb') as updates_file:
        bot.send_document(chat_id, updates_file, message_thread_id=thread_id)
            
    debug_message(message, 'Просмотрены ВСЕ обновления')
    print('Обновления Бота отосланы!')



@bot.message_handler(commands=['последнее_обновление_бота', 'last_bot_update'])
def last_updates(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id

    path_file = INFO_FOLDER + "last_bot_update.txt"
    path_photo = INFO_FOLDER + "last_bot_update.png"
    
    with open(path_file, 'r', encoding='utf-8') as updates_file:
        updates_text = updates_file.read()
    
    with open(path_photo, 'rb') as photo_file:
        bot.send_photo(chat_id, photo_file, caption=updates_text, message_thread_id=thread_id)
            
    debug_message(message, 'Просмотрено последнее обновление')
    print('Последнее обновление Бота отослано!')



@bot.message_handler(commands=['топ', 'top'])
def top_users(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id

    # Открытие базы данных с использованием контекстного менеджера
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()

        # Получаем всех пользователей с очками больше 0
        cursor.execute("SELECT id, username, name, surname, survival_points FROM users WHERE survival_points > 0")
        users = cursor.fetchall()

    # Сортировка пользователей по очкам в убывающем порядке
    sorted_users = sorted(users, key=lambda x: x[4], reverse=True)

    # Формируем топ пользователей
    top_message = "🏆 Топ пользователей, которые поделились гайдами 🏆\n\n" + "\n".join(
        f"{index}. @{user[1] if user[1] else f'{user[2]} {user[3]}'} - {user[4]} очков"
        for index, user in enumerate(sorted_users, start=1)
    )

    # Отправка сообщения
    bot.send_message(chat_id, top_message, message_thread_id=thread_id)
    debug_message(message, f"Топ пользователей отосланы по загрузке фото:")



@bot.message_handler(commands=['рейды', 'raids'])
def send_apk(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    bot.send_message(
        chat_id,
        "Скачать Базы LDoE \n\n"
        "AppGallery (Android 6.0):\n https://appgallery.huawei.ru/app/C111738085\n"
        "RuStore (Android 6.0):\n https://www.rustore.ru/catalog/app/com.DanlokPlay.LDoEBases\n\n"
        "Скачать Базы LDoE \n"
        "Сайт (с Android 5.1):\n https://ldoe.danlokplay.ru/Bases\n\n"
        "Чат по игре: https://t.me/LastSurvivorsLDoE\n", 
        message_thread_id=thread_id
    )
    debug_message(message, 'Отправлены ссылки на Базы LDoE')
    print('Отправлены ссылки на Базы LDoE')



#################################        СЛОЖНЫЕ ФУНКЦИИ           ##############################################

##### Загрузка Фото #####
@bot.message_handler(commands=['загрузить_фото', 'upload_photo'])
def upload_photo(message):
    if not allow_command(message):
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    
    try:
        photo = message.reply_to_message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        file = bot.download_file(file_info.file_path)
        photo_name = message.text.split(maxsplit=1)[1].strip()

        photo_name = capitalize_photo_name(photo_name)

        if os.path.exists(os.path.join(CHECK_FOLDER, f'{photo_name}.png')):
            bot.reply_to(message, f"Фотография с названием '{photo_name}' уже существует в папке проверки. Пожалуйста, укажите другое имя.", message_thread_id=thread_id)
            debug_message(message, f"Фотография с названием '{photo_name}' уже существует в папке проверки:")
            return

        file_name = os.path.join(CHECK_FOLDER, f'{photo_name}.png')

        with open(file_name, 'wb') as new_file:
            new_file.write(file)

        user_id = message.from_user.id
        user_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

        bot.send_message(chat_id, "Фотография успешно загружена. Ожидайте проверки.", message_thread_id=thread_id)
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


#####     Отправка ФОТО     ######

@bot.message_handler(commands=['фото', 'ф', 'photo', 'ph'])
def choice (message):
    if not allow_command(message):
        return
    
    chat_id = message.chat.id
    thread_id = message.message_thread_id

    if len(message.text.split()) < 2:
        bot.reply_to(message, "Вы не указали название фото.\n Примеры: /ф глок, /ф доставки", message_thread_id=thread_id)
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
                bot.send_photo(message.chat.id, photo_file, f'{photo_name}', message_thread_id=thread_id)

        # Отправляем уведомление
        print('Фото отослано!')
        debug_message(message, f'Фото {photo_name} было просмотрено')

    except FileNotFoundError:
        bot.reply_to(message, f"Фотография с названием '{photo_name}' не найдена.\nДля просмотра доступных фото напишите команду /кеф\n Примеры: /ф глок, /ф доставки", message_thread_id=thread_id)
        debug_message(message, f'Нет фотографии с названием {photo_name}')
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}", message_thread_id=thread_id)

def find_photo_in_folders(photo_name, folder):
    found_files = []

    # Игнорируем папку "check"
    if folder.endswith("check"):
        return found_files

    # Регулярное выражение для поиска файла с точным именем (игнорирование регистра)
    pattern = re.compile(f"^{re.escape(photo_name)}\.png$", re.IGNORECASE)

    # Перебираем файлы в текущей папке
    for filename in os.listdir(folder):
        if pattern.match(filename):  # Ищем точное совпадение с именем файла
            found_files.append(os.path.join(folder, filename))

    # Перебираем подпапки и ищем в них
    subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]
    for subfolder in subfolders:
        found_files += find_photo_in_folders(photo_name, subfolder)

    return found_files





#####    ПРОВЕРКА Обновлений на СЕРВЕРЕ   ##########

def download_and_extract_gz(url, output_file):
    """Скачивает и разархивирует .gz файл, возвращает JSON-данные."""
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(gzip.decompress(response.content))
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def get_latest_versions():
    """Получает информацию о последних версиях и их патчах."""
    config_file = os.path.join(UPDATE_FOLDER, "ldoez_config.json")
    config_data = download_and_extract_gz(CONFIG_URL, config_file)
    if not config_data:
        return None

    versions_info = []
    for version_number, details in config_data.get("versions", {}).items():
        version_code = details.get("version_code", "Unknown")
        tag = details.get("tag", "Unknown")
        patch_urls = details.get("patch_note_urls", [])

        if patch_urls:
            patch_file_url = patch_urls[0]
            patch_version = patch_file_url.split("/")[-1].split(".")[0]  # Получаем "pXXX"

            patch_file = os.path.join(UPDATE_FOLDER, f"{patch_version}.json")
            patch_data = download_and_extract_gz(patch_file_url, patch_file) or {}

            versions_info.append({
                "version_code": version_code,
                "tag": tag,
                "version_number": version_number,  # Сохраняем номер версии
                "patch_version": patch_version,
                "patch_data_ru": patch_data.get("Russian", "Нет данных"),
                "patch_data_us": patch_data.get("English", "No data")
            })

    return versions_info


def send_update_message(chat_id, versions, thread_id):
    """Формирует и отправляет сообщение с информацией об обновлениях."""
    message = ""
    for version in versions:
        message += (
            f"<b>Версия:</b> {version['version_code']}\n"
            f"<b>Тег:</b> {version['tag']}\n"
            f"<b>Обновление:</b> {version['version_number']}\n"  # Теперь выводим номер версии
            f"<b>Патч:</b> {version['patch_version']}\n"
            f"🇷🇺 <b>RU:</b> {version['patch_data_ru']}\n"
            f"🇺🇸 <b>US:</b> {version['patch_data_us']}\n\n"
        )

    bot.send_message(chat_id, message, parse_mode="HTML", message_thread_id=thread_id)


@bot.message_handler(commands=['update', 'обновление'])
def handle_update_command(message):
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    versions = get_latest_versions()
    if versions:
        send_update_message(chat_id, versions, thread_id)
    else:
        bot.send_message(chat_id, "Не удалось получить информацию об обновлениях.")



##################                Только РАЗРАБОТЧИКА                #####################

@bot.message_handler(commands=['записать_коды'])
def write_codes(message):
    handle_message(message)

    thread_id = message.message_thread_id
    
    if message.from_user.id != DEVELOPER_ID:
        bot.reply_to(message, "Извините, у вас нет прав на выполнение этой команды.", message_thread_id=thread_id)
        debug_message(message, 'Попытался записать коды: ')
        return

    if not message.reply_to_message or not message.reply_to_message.text:
        bot.reply_to(message, "Не найдено сообщение для записи в файл.", message_thread_id=thread_id)
        debug_message(message, 'Не найдено сообщение для записи в файл кодов: ')
        return

    try:
        codes_text = message.reply_to_message.text.strip()
        lines = codes_text.split('\n')

        year = lines[0].strip()
        month = lines[1].strip()
        codes = '\n'.join(lines[2:]).strip()

        filename = 'codes.json.gz'
        try:
            with gzip.open(filename, 'rt', encoding='utf-8') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            data = {}

        # Создаем структуру, если её нет
        if year not in data:
            data[year] = {}
        if month not in data[year]:
            data[year][month] = {}

        # Очистим старые дубли перед записью
        month_data = {}

        # Обрабатываем коды
        codes_lines = codes.split('\n')
        for line in codes_lines:
            parts = line.split(' : ')
            if len(parts) == 2:
                code_range, code = parts
                code = code.strip()
                code_range = code_range.strip()

                if '-' in code_range:
                    start, end = map(int, code_range.split('-'))
                    for i in range(start, end + 1):
                        month_data[str(i)] = code
                else:
                    month_data[str(int(code_range))] = code
            else:
                bot.reply_to(message, f"Ошибка в строке: {line}. Ожидаемый формат: 'диапазон : код'", message_thread_id=thread_id)

        # Заменяем старые данные новыми (избавляемся от дубликатов)
        data[year][month] = month_data

        # Записываем JSON в сжатый файл (с отступами)
        with gzip.open(filename, 'wt', encoding='utf-8') as file:
            json.dump(data, file, indent=4)  # Без сжатия строк, но в gzip

        bot.reply_to(message, "Коды успешно записаны в файл (gzip).", message_thread_id=thread_id)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при записи кодов в файл: {e}", message_thread_id=thread_id)

    print('Коды записаны (gzip)!')
    debug_message(message, 'Коды были записаны в файл:')





@bot.message_handler(commands=['перезаписать', 'rewrite'])
def handle_rewrite_command(message):
    handle_message(message)

    thread_id = message.message_thread_id

    try:
        if message.from_user.id != DEVELOPER_ID:
            bot.reply_to(message, "У вас нет прав для использования этой команды.", message_thread_id=thread_id)
            debug_message(message, f"Попытался использовать команду /перезаписать")
            return

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Photos", callback_data="rewrite_photos"))
        keyboard.add(types.InlineKeyboardButton(text="Videos", callback_data="rewrite_videos"))
        
        bot.send_message(message.chat.id, "Выберите файл для перезаписи:", reply_markup=keyboard, message_thread_id=thread_id)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}", message_thread_id=thread_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('rewrite_'))
def handle_rewrite_callback(call):
    thread_id = call.message.message_thread_id 

    try:
        if call.from_user.id != DEVELOPER_ID:
            bot.answer_callback_query(call.id, "У вас нет прав для использования этой команды.")
            debug_message(call.message, f"Попытался изменить файл")
            return

        if call.data == 'rewrite_photos':
            file_path = 'photos.txt'
        elif call.data == 'rewrite_videos':
            file_path = 'videos.txt'
        else:
            bot.answer_callback_query(call.id, "Неверный выбор.")
            debug_message(call.message, f"Неверный выбор файла для его перезаписи")
            return

        current_content = read_file_content(file_path)

        # Отправка текущего содержимого файла пользователю
        bot.send_message(call.message.chat.id, f"{current_content}", message_thread_id=thread_id)
        
        # Запрос нового содержимого у пользователя
        bot.send_message(call.message.chat.id, f"Отправьте новое содержимое для файла {file_path}.", message_thread_id=thread_id)
        bot.register_next_step_handler(call.message, process_new_content, file_path, thread_id)
    
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Произошла ошибка: {e}", message_thread_id=thread_id)

def process_new_content(message, file_path, thread_id):
    try:
        new_content = message.text.strip()

        rewrite_file(file_path, new_content)
        bot.reply_to(message, f"Файл {file_path} успешно перезаписан.", message_thread_id=thread_id)
        debug_message(message, f"Файл {file_path} успешно перезаписан")
    
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при перезаписи файла: {e}", message_thread_id=thread_id)




# Функция, которая будет выполняться
def scheduled_task():
    print("⏳ Начинаем выполнение запланированной задачи...")
    try:
        download_image()
        process_image()
        print("✅ Задача выполнена успешно!")
    except Exception as e:
        print(f"❌ Ошибка при выполнении задачи: {e}")

# Функция для расчёта следующей даты задачи
def schedule_next_run():
    now = datetime.now()
    # Находим 1-е число следующего месяца
    next_month = now.replace(day=28) + timedelta(days=4)
    first_day_next_month = next_month.replace(day=1)

    # Дата, когда надо запустить задачу — за 1 день до нового месяца
    run_date = first_day_next_month - timedelta(days=1)
    run_time = run_date.replace(hour=12, minute=0, second=0, microsecond=0)  # например, в 12:00 дня

    print(f"⏰ Следующая задача запланирована на: {run_time}")

    scheduler.add_job(scheduled_task, trigger='date', run_date=run_time, id='monthly_task')

# Старт планировщика
scheduler.start()
schedule_next_run()




# Создение БД
def init_db():
    # Создаёт таблицу пользователей (вызывать при запуске бота)
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
        conn.commit()

#######################################                       СТАРТ БОТА             ###################################
# Бот запущен
print('OK')

# Вывод времени при старте бота
print("Текущее время: ", get_current_time_in_timezone())

bot.infinity_polling(none_stop=True)