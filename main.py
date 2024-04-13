from config import *
from datetime import datetime
import time
import requests
from random import randint

import telebot


token = API_TOKEN
bot = telebot.TeleBot(token)

def set_webhook_with_delay():
    time.sleep(1)
    bot.set_webhook()


API_URL = "https://api.telegram.org/bot{}/sendMessage".format(token)

print('OK')

def send_message_with_retry(chat_id, text):
    retries = 3
    delay = 1  # Initial delay in seconds

    for _ in range(retries):
        response = requests.post(API_URL, data={"chat_id": chat_id, "text": text})
        if response.status_code == 200:
            return
        elif response.status_code == 429:
            print("Rate limit exceeded. Retrying after {} seconds.".format(delay))
            time.sleep(delay)
            delay *= 2  # Exponential backoff
        else:
            # Handle other types of errors
            print("Unexpected error:", response.status_code)
            return

    print("Max retries exceeded. Unable to send message.")



@bot.message_handler(commands=['info', 'инфо'])
def start_info(message):
    bot.send_message(message.chat.id, '/код(к) - код на сегодня от БА\n/доп_инфо(ди)', reply_to_message_id=message.id)
        
    chat_name = message.chat.title if message.chat.title else message.chat.username
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    notification_text = f'(!инфо) Информация о командах просмотрена @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
    bot.send_message(1375077159, notification_text, parse_mode='HTML')
    print("Информация о командах выслана!")


@bot.message_handler(commands=['additional_info', 'допинфа', 'ди', 'допинфо', 'доп_инфо', 'долнительная_информация', 'информация'])
def start_additional_info(message):
    bot.send_message(message.chat.id, '/коды - коды на текущий месяц \n/фото(ф) название_фото - отсылает нужную фотографию \n/кеф(пр_фото) - отсылает все существующие названия фото, которые загружены \n/монета(м) - подросить монету (Орёл или Решка) \n/записать_коды (YYYY_MM; D:CODE)(только @DanlokPlay) \n/загрузить_фото "название фото" (Для кодов: Месяц Год)(только @DanlokPlay)', reply_to_message_id=message.id)
    #\n/загрузить_фото название фото (Для кодов EN: codes_mounth_year)(только @DanlokPlay)
    chat_name = message.chat.title if message.chat.title else message.chat.username
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    notification_text = f'(!инфо) Информация о Дополнительных командах просмотрена @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
    bot.send_message(1375077159, notification_text, parse_mode='HTML')
    print("Информация о Дополнительных командах выслана!")

def read_codes_from_file(filename):
    codes = {}
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                year_month, codes_str = line.strip().split('::')
                year, month = map(int, year_month.split('_'))
                
                day_codes = {}
                for day_code in codes_str.split(','):
                    day, code = day_code.split(':')
                    day_codes[int(day)] = code
                codes[(year, month)] = day_codes
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except ValueError:
        print(f"Invalid data format in '{filename}'.")
    
    return codes

codes = read_codes_from_file('codes.txt')


@bot.message_handler(commands=['код', 'к', 'пароль', 'k', 'kod', 'code', 'password'])
def start_code(message):
    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_day = current_datetime.day
    current_year = current_datetime.year
    daily_code = None

    if (current_year, current_month) in codes:
        day_codes = codes[(current_year, current_month)]
        if current_day in day_codes:
            daily_code=day_codes[current_day]
            send_message_with_retry(message.chat.id, daily_code)

    chat_name = message.chat.title if message.chat.title else message.chat.username
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    notification_text = f'(!код) Код на сегодня был просмотрен @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
    bot.send_message(1375077159, notification_text, parse_mode='HTML')
    print("Пароль на сегодня выслан!", current_day, ':', daily_code)


@bot.message_handler(commands=['коды', 'коды_на_месяц', 'месяц', 'бункер', 'бункер_альфа', 'codes'])
def start_codes(message):
    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_year = current_datetime.year

    print(current_month)

    if current_month == 1:
        filename = f'Январь {current_year}.png'
        month_name = 'Январь'
    elif current_month == 2:
        filename = f'Февраль {current_year}.png'
        month_name = 'Февраль'
    elif current_month == 3:
        filename = f'Март {current_year}.png'
        month_name = 'Март'
    elif current_month == 4:
        filename = f'Апрель {current_year}.png'
        month_name = 'Апрель'
    elif current_month == 5:
        filename = f'Май {current_year}.png'
        month_name = 'Май'
    elif current_month == 6:
        filename = f'Июнь {current_year}.png'
        month_name = 'Июнь'
    elif current_month == 7:
        filename = f'Июль {current_year}.png'
        month_name = 'Июль'
    elif current_month == 8:
        filename = f'Август {current_year}.png'
        month_name = 'Август'
    elif current_month == 9:
        filename = f'Сентябрь {current_year}.png'
        month_name = 'Сентябрь'
    elif current_month == 10:
        filename = f'Октябрь {current_year}.png'
        month_name = 'Октябрь'
    elif current_month == 11:
        filename = f'Ноябрь {current_year}.png'
        month_name = 'Ноябрь'
    elif current_month == 12:
        filename = f'Декабрь {current_year}.png'
        month_name = 'Декабрь'
    else:
        filename = ''
        month_name = ''
    
    if filename:
        with open(filename, 'rb') as file:
            bot.send_photo(message.chat.id, file, f'Коды на {month_name} {current_year}')
    
    chat_name = message.chat.title if message.chat.title else message.chat.username
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    notification_text = f'(!коды) Коды на {month_name} были просмотрены @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
    bot.send_message(1375077159, notification_text, parse_mode='HTML')
    print("Пароли на месяцы высланы!")

@bot.message_handler(commands=['м', 'монета', 'coin'])
def start_coins(message):
    var = randint(0, 1)
    heads = 'Орёл'
    tails = 'Решка'
    if var == 0:
        bot.send_message(message.chat.id, f'{heads}', reply_to_message_id=message.id)

        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'(!монета) Монета подброшена @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a> и выпал {heads}'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
        print(f"Подброс монеты сработал! ({heads})")
    else:
        bot.send_message(message.chat.id, f'{tails}', reply_to_message_id=message.id)

        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'(!монета) Монета подброшена @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a> и выпала {tails}'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
        print(f"Подброс монеты сработал! ({tails})")

# Сначала записать коды, потом с упоминанием этого сообщения выполнить команду
@bot.message_handler(commands=['записать_коды'])
def write_codes(message):
    # Проверяем, что пользователь, вызвавший команду, является администратором
    if message.from_user.id != 1375077159:
        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'@{username} попытался записать коды в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
        bot.reply_to(message, "Извините, у вас нет прав на выполнение этой команды.")
        return

    # Проверяем, что в сообщении, содержащем команду, есть данные для записи
    if not message.reply_to_message or not message.reply_to_message.text:
        bot.reply_to(message, "Не найдено сообщение для записи в файл.")
        return

    # Получаем текст сообщения, на которое был отправлен ответ, и добавляем символ новой строки
    codes_text = message.reply_to_message.text.strip()
    year_month, codes = codes_text.split('\n', 1)  # Разделяем год_месяц и коды
    codes = codes.replace('\n', ',')  # Заменяем символы новой строки на запятые
    codes_text = '\n' + f'{year_month}::{codes}'  # Форматируем строку с кодами

    # Записываем полученные коды в файл
    filename = 'codes.txt'
    try:
        with open(filename, 'a') as file:
            file.write(codes_text + '\n')
        bot.reply_to(message, "Коды успешно записаны в файл.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при записи кодов в файл: {e}")

    # Отправляем уведомление об успешной записи кодов
    chat_name = message.chat.title if message.chat.title else message.chat.username
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    notification_text = f'Коды были записаны в файл @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
    bot.send_message(1375077159, notification_text, parse_mode='HTML')
    print('Коды записаны!')

@bot.message_handler(commands=['загрузить_фото'])
def upload_photo(message):

    if message.from_user.id != 1375077159:
        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'@{username} попытался загрузить фото в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
        bot.reply_to(message, "Извините, у вас нет прав на выполнение этой команды.")
        return
    # Check if command is issued with correct format
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Неправильный формат команды. Пожалуйста, укажите название фото.")
        return

    # Splitting the command into parts
    command_parts = message.text.split(maxsplit=1)[1].split()
    
    # Checking if the command is in the format "Месяц год"
    if len(command_parts) == 2 and command_parts[0].capitalize() in ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']:
        try:
            # Получаем информацию о файле фотографии
            photo = message.reply_to_message.photo[-1]
            file_info = bot.get_file(photo.file_id)

            # Скачиваем фото
            file = bot.download_file(file_info.file_path)

            # Получаем название фото и комментарий из аргументов команды
            photo_args = message.text.split(maxsplit=1)[1].split('-', 1)  # Название фото и комментарий
            photo_name = photo_args[0].strip()  # Название фото
            comment = photo_args[1].strip() if len(photo_args) > 1 else ''  # Комментарий

            # Генерируем имя файла для сохранения
            file_name = f'{photo_name}.png'

            # Сохраняем фото на сервере
            with open(file_name, 'wb') as new_file:
                new_file.write(file)

            # Отправляем подтверждение о загрузке
            bot.reply_to(message, "Фотография успешно загружена.")

            # Отправляем уведомление об успешной загрузке фотографии
            chat_name = message.chat.title if message.chat.title else message.chat.username
            username = message.from_user.username if message.from_user.username else message.from_user.first_name
            notification_text = f'Коды на "{photo_name}" были загружены @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
            bot.send_message(1375077159, notification_text, parse_mode='HTML')
            print('Коды на месяц загружены!')

        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка при загрузке фотографии: {e}")
        
    else:
        # Rest of the upload_photo function remains unchanged
        try:
            # Получаем информацию о файле фотографии
            photo = message.reply_to_message.photo[-1]
            file_info = bot.get_file(photo.file_id)

            # Скачиваем фото
            file = bot.download_file(file_info.file_path)

            # Получаем название фото и комментарий из аргументов команды
            photo_args = message.text.split(maxsplit=1)[1].split('-', 1)  # Название фото и комментарий
            photo_name = photo_args[0].strip()  # Название фото
            comment = photo_args[1].strip() if len(photo_args) > 1 else ''  # Комментарий

            # Генерируем имя файла для сохранения
            file_name = f'{photo_name}.png'
            file_name = file_name.capitalize()

            # Сохраняем фото на сервере
            with open(file_name, 'wb') as new_file:
                new_file.write(file)

            # Добавляем название фото и комментарий в текстовый файл
            with open('uploaded_photos.txt', 'a', encoding='utf-8') as txt_file:
                txt_file.write(f"/ф {photo_name} - {comment}\n")

            # Отправляем подтверждение о загрузке
            bot.reply_to(message, "Фотография успешно загружена.")

            # Отправляем уведомление об успешной загрузке фотографии
            chat_name = message.chat.title if message.chat.title else message.chat.username
            username = message.from_user.username if message.from_user.username else message.from_user.first_name
            notification_text = f'Фотография "{photo_name}" была загружена @{username} в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
            bot.send_message(1375077159, notification_text, parse_mode='HTML')
            print('Фотография загружена!')
        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка при загрузке фотографии: {e}")


@bot.message_handler(commands=['фото', 'ф', 'photo', 'ph'])
def send_photo_by_name(message):
    # Проверяем, что команда содержит аргументы
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Вы не указали название фото. Пожалуйста, попробуйте снова.")
        return

    try:
        # Получаем название фото из аргументов команды
        photo_name = message.text.split(maxsplit=1)[1].capitalize()  # Название фото
        
        Temp = photo_name + ".png"

        # Приводим название фото и строки из файла к нижнему регистру для сравнения
        photo_name_lower = photo_name.lower()

        # Выбор файла в зависимости от наличия слова "моды" в команде
        file_to_read = 'uploaded_photos.txt'
        if 'моды' in message.text.lower():
            file_to_read = 'weapons.txt'
            if 'моды на' in message.text.lower():
                photo_name = 'Моды ' + photo_name.split('Моды на ')[1]
                photo_name_lower = photo_name.lower()

        # Читаем строки из файла и ищем совпадение с photo_name
        with open(file_to_read, 'r', encoding='utf-8') as text_file:
            for line in text_file:
                if photo_name_lower in line.lower():
                    found_line = line.strip()
                    break
            else:
                raise FileNotFoundError

        # Отправляем фото пользователю
        file_name = f'{photo_name}.png'  # Имя файла
        with open(file_name, 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file, f"{found_line}")

        # Отправляем уведомление
        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'@{username} просмотрел фото "{file_name}" в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
        print('Фото отослано!')

    except FileNotFoundError:
        bot.reply_to(message, f"Фотография с названием '{photo_name}' не найдена. Для просмотра доступных фото напиши команду /кеф")
        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'@{username} Хотел просмотреть фото "{Temp}" в чате <a href="https://t.me/{chat_name}">{chat_name}</a>, но её не оказалось!'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")


@bot.message_handler(commands=['КЕФ', 'пр_фото', 'пример_фото', 'пр_ф', 'пф', 'кеф', 'kef'])
def list_uploaded_photos(message):
    try:
        # Читаем содержимое файла с названиями фотографий
        with open('uploaded_photos.txt', 'r', encoding='utf-8') as txt_file:
            photo_names = txt_file.readlines()

        # Проверяем, есть ли хотя бы одно название фотографии
        if photo_names:
            # Формируем строку с названиями фотографий
            photo_names_string = "".join(photo_names)
            # Отправляем названия фотографий в чат одним сообщением
            bot.send_message(message.chat.id, f"\n{photo_names_string}")
        else:
            bot.reply_to(message, "Нет загруженных фотографий.")

        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'@{username} просмотрел список фотографий в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
        print('Список названий фотографий отослан!')

    except FileNotFoundError:
        bot.reply_to(message, "Файл с названиями фотографий не найден.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при отправке названий фотографий: {e}")
        
        
@bot.message_handler(commands=['обновления', 'updates'])
def show_updates(message):
    try:
        with open('updates.txt', 'r', encoding='utf-8') as updates_file:
            updates_text = updates_file.read()
            bot.reply_to(message, updates_text)
            
        chat_name = message.chat.title if message.chat.title else message.chat.username
        username = message.from_user.username if message.from_user.username else message.from_user.first_name
        notification_text = f'@{username} просмотрел обновления бота в чате <a href="https://t.me/{chat_name}">{chat_name}</a>'
        bot.send_message(1375077159, notification_text, parse_mode='HTML')
        print('Обновления Бота отосланы!')
    except FileNotFoundError:
        bot.reply_to(message, "Файл обновлений не найден.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['echo'])
def echo_message(message):
    if message.from_user.id != 1375077159:
        var = randint(0, 2)
        if var == 0:
        	bot.reply_to(message, "У тебя нет прав. И денег тоже:D")
        if var == 1:
            bot.reply_to(message, "Бесправный получается...")
        if var == 2:
            bot.reply_to(message, "Не-а")
        return
    bot.send_message(-1001856142075, message.text.split('/echo', 1)[1].strip())
      
bot.infinity_polling()