import json
import gzip
from collections import defaultdict
import google.generativeai as genai
from datetime import datetime, timedelta

MONTHS_RU = [
    "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"
]

genai.configure(api_key="AIzaSyADRQY5Kx7KGMpYhGbMxg70kwmKny_SEB4")

def process_image():
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")

    current_date = datetime.now()
    next_month_date = current_date.replace(day=28) + timedelta(days=4)
    next_month = next_month_date.month - 1
    next_year = next_month_date.year

    filename = f"codes/{MONTHS_RU[next_month].capitalize()} {next_year}.png"
    image_path = filename

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    prompt = (
        f"The year is {next_year}\n"
        "Please read the month from the image and the codes. "
        "Return the result in the following format:\n"
        f"{next_year}\n"
        f"MM\n"
        "1 : 13831\n"
        "2-3 : 03831\n"
        "... "
    )

    response = model.generate_content(
        contents=[
            {"role": "user", "parts": [prompt]},
            {"role": "user", "parts": [{"mime_type": "image/png", "data": image_bytes}]}
        ]
    )

    month_codes = response.text
    print(month_codes)

    parsed_codes = defaultdict(lambda: defaultdict(dict))
    lines = month_codes.strip().split("\n")
    year = lines[0]
    month = lines[1]

    for line in lines[2:]:
        if " : " in line:
            days_range, code = line.split(" : ")
            days = days_range.split("-")
            if len(days) == 1:
                day = days[0]
                parsed_codes[year][month][day] = code
            else:
                start_day = int(days[0])
                end_day = int(days[1])
                for day in range(start_day, end_day + 1):
                    parsed_codes[year][month][str(day)] = code

    try:
        with gzip.open('codes.json.gz', 'rt', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    if year not in existing_data:
        existing_data[year] = {}

    existing_data[year][month] = parsed_codes[year][month]

    with gzip.open('codes.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

    print("✅ Данные успешно обновлены в codes.json.gz")
