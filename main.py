import telebot
from datetime import datetime
import time
import requests
from random import randint

token = '6064246639:AAE-9Np2IM6rSAXlCOoxql6rgeLNd1QKcZI'
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


def read_codes_from_file(filename):
    codes = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                day, code = line.strip().split(':')
                codes[int(day)] = code
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except ValueError:
        print(f"Invalid data format in '{filename}'.")
    
    return codes

codes = read_codes_from_file('codes.txt')


@bot.message_handler(commands=['код', 'к', 'пароль', 'k', 'kod', 'code', 'password'])
def start_code(message):
    current_datetime = datetime.now()
    current_datetime_DAY = current_datetime.day

    if current_datetime_DAY in codes:
        send_message_with_retry(message.chat.id, codes[current_datetime_DAY])

    send_message_with_retry(1375077159, 'Кто-то посмотрел код на сегодня (!код)')
    print("Пароль на сегодня выслан!")


@bot.message_handler(commands=['коды', 'коды_на_месяц', 'месяц', 'бункер', 'бункер_альфа'])
def start_codes(message):
    try:
        with open('photo.jpg', 'rb') as file:
            bot.send_photo(message.chat.id, file, 'Коды на этот месяц')
    except FileNotFoundError:
        print("Image file 'photo.jpg' not found.")
    
    send_message_with_retry(1375077159, 'Кто-то посмотрел коды на месяц (!коды)')
    print("Пароли на месяцы высланы!")

@bot.message_handler(commands=['м', 'монета'])
def start_coins(message):
    var = randint(0, 1)
    if var == 0:
        bot.send_message(message.chat.id, 'Орёл', reply_to_message_id=message.id)
        send_message_with_retry(1375077159, 'Кто-то подбросил монету и выпал Орёл! (!монета)')
    else:
        bot.send_message(message.chat.id, 'Решка', reply_to_message_id=message.id)
        send_message_with_retry(1375077159, 'Кто-то подбросил монету и выпала Решка! (!монета)')
    print("Подброс монеты сработал!")

@bot.message_handler(commands=['info', 'инфо'])
def start_info(message):
    bot.send_message(message.chat.id, '/код(к, пароль, k, kode, code, password) - код на сегодня от БА \n/коды - коды на текущий месяц \n/монета(м) - подросить монету (Орёл или Решка) P.S. для важных решений:D ', reply_to_message_id=message.id)
    bot.send_message(1375077159, 'Кто-то запросил список команд (!инфо)')
    print("Информация о командах выслана!")

bot.infinity_polling()