import requests
import os
from datetime import datetime, timedelta

MONTHS_RU = [
    "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"
]

EWOSVOI_USER_TOKEN = "MTIwNzM3OTk0NDk1OTY0MzY1OA.GlDYE9.ELd83I-_Yhp3GKp_gYApnPKuosq7fit3-cEsj8"
DISCORD_LDOE_CHANNEL_ID = "941218328943403028"

def download_image():
    headers = {
        "Authorization": EWOSVOI_USER_TOKEN,
        "User-Agent": "Mozilla/5.0"
    }

    url = f"https://discord.com/api/v9/channels/{DISCORD_LDOE_CHANNEL_ID}/pins"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        messages = response.json()
        messages.sort(key=lambda x: x['timestamp'], reverse=True)

        current_date = datetime.now()
        next_month_date = current_date.replace(day=28) + timedelta(days=4)
        next_month = next_month_date.month - 1
        next_year = next_month_date.year

        filename = f"{MONTHS_RU[next_month].capitalize()} {next_year}.png"

        for msg in messages:
            attachments = msg.get("attachments", [])
            for attachment in attachments:
                file_url = attachment["url"]
                if attachment.get("content_type") and "image" in attachment["content_type"]:
                    print(f"Скачиваю: {file_url}")
                    os.makedirs("codes", exist_ok=True)
                    img_data = requests.get(file_url).content
                    with open(os.path.join("codes", filename), "wb") as f:
                        f.write(img_data)
                    print("✅ Изображение загружено.")
                    return  # Завершаем функцию после первой картинки
        print("❌ Не найдено закреплённых сообщений с изображениями.")
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
