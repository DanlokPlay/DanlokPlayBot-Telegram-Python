import telebot

from datetime import datetime


bot = telebot.TeleBot('6064246639:AAE-9Np2IM6rSAXlCOoxql6rgeLNd1QKcZI')

"""
# DanlokPlay
CHAT_ID = 1375077159

# KatomanD
CHAT_ID = -1001969870941

# Pechka TV
CHAT_ID = 

# message.chat.id - во всех чатах. -> CHAT_ID - определённый чат

"""
# Реагирует на сообщение ( это у нас 1), а не на команду (начинается на /)
"""
@bot.message_handler(func = lambda message: message.text == '1')
def start(message):
    bot.send_message(message.chat.id, '2!')
"""
#Отправка в чат (определённый) (с упоминанием) send_message((CHAT_ID) message.chat.id, сообщение, (ответ на сообщение) reply_to_message_id = message.id)

@bot.message_handler(commands=['код', 'к', 'пароль', 'k', 'kod'])
def start(message):
    current_datetime = datetime.now()
    current_datetime_DAY = current_datetime.day
    '''
    if (current_datetime_DAY == 1 or current_datetime_DAY == 2):
        bot.send_message(message.chat.id, '12')
    if (current_datetime_DAY == 3 or current_datetime_DAY == 4):
        bot.send_message(message.chat.id, '34')
    if (current_datetime_DAY == 5 or current_datetime_DAY == 6):
        bot.send_message(message.chat.id, '56')
    if (current_datetime_DAY == 7 or current_datetime_DAY == 8):
        bot.send_message(message.chat.id, '78')
    if (current_datetime_DAY == 9 or current_datetime_DAY == 10):
        bot.send_message(message.chat.id, '910')
    if (current_datetime_DAY == 11 or current_datetime_DAY == 12):
        bot.send_message(message.chat.id, '1112')
    if (current_datetime_DAY == 12 or current_datetime_DAY == 14):
        bot.send_message(message.chat.id, '1314')
    if (current_datetime_DAY == 15 or current_datetime_DAY == 16):
        bot.send_message(message.chat.id, '1516')
    if (current_datetime_DAY == 17 or current_datetime_DAY == 18):
        bot.send_message(message.chat.id, '1718')
    if (current_datetime_DAY == 19 or current_datetime_DAY == 20):
        bot.send_message(message.chat.id, '1920', reply_to_message_id = message.id)
    if (current_datetime_DAY == 21 or current_datetime_DAY == 22):
        bot.send_message(message.chat.id, '2122')
    if (current_datetime_DAY == 23 or current_datetime_DAY == 24):
        bot.send_message(message.chat.id, '2324')
    if (current_datetime_DAY == 25 or current_datetime_DAY == 26):
        bot.send_message(message.chat.id, '2526')
    if (current_datetime_DAY == 27 or current_datetime_DAY == 28):
        bot.send_message(message.chat.id, '2728')
    if (current_datetime_DAY == 29 or current_datetime_DAY == 30):
        bot.send_message(message.chat.id, '2930')
    if (current_datetime_DAY == 31):
        bot.send_message(message.chat.id, '2930')
    '''
    if (current_datetime_DAY == 1):
        bot.send_message(message.chat.id, '79230', reply_to_message_id = message.id)
    if (current_datetime_DAY == 2 or current_datetime_DAY == 3):
        bot.send_message(message.chat.id, '96148', reply_to_message_id = message.id)
    if (current_datetime_DAY == 4 or current_datetime_DAY == 5):
        bot.send_message(message.chat.id, '65806', reply_to_message_id = message.id)
    if (current_datetime_DAY == 6 or current_datetime_DAY == 7):
        bot.send_message(message.chat.id, '52021', reply_to_message_id = message.id)
    if (current_datetime_DAY == 8 or current_datetime_DAY == 9):
        bot.send_message(message.chat.id, '21815', reply_to_message_id = message.id)
    if (current_datetime_DAY == 10 or current_datetime_DAY == 11):
        bot.send_message(message.chat.id, '18336', reply_to_message_id = message.id)
    if (current_datetime_DAY == 12 or current_datetime_DAY == 13):
        bot.send_message(message.chat.id, '80418', reply_to_message_id = message.id)
    if (current_datetime_DAY == 14 or current_datetime_DAY == 15):
        bot.send_message(message.chat.id, '08007', reply_to_message_id = message.id)
    if (current_datetime_DAY == 16 or current_datetime_DAY == 17):
        bot.send_message(message.chat.id, '83286', reply_to_message_id = message.id)
    if (current_datetime_DAY == 18 or current_datetime_DAY == 19):
        bot.send_message(message.chat.id, '34164', reply_to_message_id = message.id)
    if (current_datetime_DAY == 20 or current_datetime_DAY == 21):
        bot.send_message(message.chat.id, '40314', reply_to_message_id = message.id)
    if (current_datetime_DAY == 22 or current_datetime_DAY == 23):
        bot.send_message(message.chat.id, '02157', reply_to_message_id = message.id)
    if (current_datetime_DAY == 24 or current_datetime_DAY == 25):
        bot.send_message(message.chat.id, '21066', reply_to_message_id = message.id)
    if (current_datetime_DAY == 26 or current_datetime_DAY == 27):
        bot.send_message(message.chat.id, '13888', reply_to_message_id = message.id)
    if (current_datetime_DAY == 28 or current_datetime_DAY == 29):
        bot.send_message(message.chat.id, '31673', reply_to_message_id = message.id)
    if (current_datetime_DAY == 30 or current_datetime_DAY == 31):
        bot.send_message(message.chat.id, '10162', reply_to_message_id = message.id)

@bot.message_handler(commands=['коды', 'коды_на_месяц', 'месяц', 'бункер', 'бункер_альфа'])
def start(message):
    file = open('photo.jpg', 'rb')
    bot.send_photo(message.chat.id, file, 'Коды на этот месяц')
"""
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет!')

@bot.message_handler(commands=['прив'])
def start(message):
    bot.reply_to(message, 'Привет!')

@bot.message_handler(commands=['end'])
def start(message):
    bot.send_message(message.chat.id, 'Пока!')
"""
@bot.message_handler(commands=['chat_id'])
def start(message):
    bot.send_message(message.chat.id, message.chat.id)

@bot.message_handler(commands=['my_nick'])
def start(message):
    bot.send_message(message.chat.id, message.from_user.username)


bot.polling()