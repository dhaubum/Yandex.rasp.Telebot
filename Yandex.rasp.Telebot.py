import telebot
import requests

bot = telebot.TeleBot('TOKEN-TelegramBot')
API = ('API-yandex.rasp')

def load_station_codes(file_path):
    station_codes = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                station_name = parts[0].strip()
                station_code = parts[1].strip()
                station_codes[station_name] = station_code
    return station_codes

pinned_messages = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global pinned_messages

    if message.chat.id in pinned_messages:
        bot.unpin_chat_message(message.chat.id, pinned_messages[message.chat.id])
        del pinned_messages[message.chat.id]

    message_text = "Привет! Я бот для поиска рейсов поездов. Просто введите /rasp чтобы получить расписание.\n\n"
    message_text += "/help\n\n"
    message_text += "Данные предоставлены сервисом [Яндекс.Расписания](http://rasp.yandex.ru/)"
    sent_message = bot.send_message(message.chat.id, message_text, parse_mode="Markdown")

    bot.pin_chat_message(sent_message.chat.id, sent_message.message_id)
    pinned_messages[message.chat.id] = sent_message.message_id

@bot.message_handler(commands=['help'])
def send_help(message):
    message_text = "Просто введите /rasp чтобы получить расписание.\n"
    message_text += "Данные предоставлены сервисом [Яндекс.Расписания](http://rasp.yandex.ru/)"
    bot.send_message(message.chat.id, message_text, parse_mode="Markdown")

@bot.message_handler(commands=['rasp'])
def get_routes(message):
    try:
        bot.reply_to(message, "Введите название пункта отправления:")
        bot.register_next_step_handler(message, ask_from_station)
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка')
        bot.send_message(message.chat.id, "Чтобы получить другое расписание, воспользуйтесь командой /rasp")

def ask_from_station(message):
    try:
        from_station = message.text.lower()
        bot.reply_to(message, "Введите название пункта прибытия:")
        bot.register_next_step_handler(message, lambda m: ask_to_station(from_station, m))
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка')
        bot.send_message(message.chat.id, "Чтобы получить другое расписание, воспользуйтесь командой /rasp")

def ask_to_station(from_station, message):
    try:
        to_station = message.text.lower()
        bot.reply_to(message, "Введите дату в формате YYYY-MM-DD:")
        bot.register_next_step_handler(message, lambda m: ask_date(from_station, to_station, m))
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка')
        bot.send_message(message.chat.id, "Чтобы получить другое расписание, воспользуйтесь командой /rasp")

def ask_date(from_station, to_station, message):
    try:
        date = message.text
        bot.reply_to(message, "Введите временной промежуток в формате HH:MM-HH:MM:")
        bot.register_next_step_handler(message, lambda m: ask_time_range(from_station, to_station, date, m))
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка')
        bot.send_message(message.chat.id, "Чтобы получить другое расписание, воспользуйтесь командой /rasp")

def ask_time_range(from_station, to_station, date, message):
    try:
        time_range = message.text
        station_codes = load_station_codes('station_codes.txt')

        from_station_code = station_codes.get(from_station)
        to_station_code = station_codes.get(to_station)

        start_time, end_time = time_range.split('-')

        if not from_station_code:
            bot.reply_to(message, f"Код для станции {from_station} не найден.")
            return
        if not to_station_code:
            bot.reply_to(message, f"Код для станции {to_station} не найден.")
            return

        time_interval = f"{date}T{start_time}:00%2B03:00--{date}T{end_time}:00%2B03:00"

        url = f"https://api.rasp.yandex.net/v3.0/search/?apikey={API}&format=json&from={from_station_code}&to={to_station_code}&date={date}&interval={time_interval}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if 'segments' in data:
            routes = data['segments']
            routes_to_send = []

            for route in routes:
                departure_time = route['departure'].split('T')[1][:5]
                arrival_time = route['arrival'].split('T')[1][:5]
                if start_time <= departure_time <= end_time and start_time <= arrival_time <= end_time:
                    route_info = f"Номер рейса: {route['thread']['number']}\n"
                    route_info += f"Отправление: {route['from']['title']}\n"
                    route_info += f"Дата отправления: {route['start_date']}\n"
                    route_info += f"Время отправления: {departure_time}\n"
                    route_info += f"Прибытие: {route['to']['title']}\n"
                    route_info += f"Время прибытия: {arrival_time}\n"
                    route_info += f"Продолжительность: {route['duration'] // 60} минут\n"
                    route_info += f"Остановки: {route['stops']}\n"
                    route_info += "---------------------------------------"
                    routes_to_send.append(route_info)

                    if len(routes_to_send) == 5:
                        message_text = "\n".join(routes_to_send)
                        bot.send_message(message.chat.id, message_text, parse_mode="Markdown")
                        routes_to_send = []

            if routes_to_send:
                message_text = "\n".join(routes_to_send)
                bot.send_message(message.chat.id, message_text, parse_mode="Markdown")

            if not any(start_time <= route['departure'].split('T')[1][:5] <= end_time and start_time <=
                       route['arrival'].split('T')[1][:5] <= end_time for route in routes):
                bot.reply_to(message, "По вашему запросу рейсы не найдены.")
        else:
            bot.reply_to(message, "По вашему запросу рейсы не найдены.")

        bot.send_message(message.chat.id, "Чтобы получить другое расписание, воспользуйтесь командой /rasp")


    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка")
        bot.send_message(message.chat.id, "Чтобы получить другое расписание, воспользуйтесь командой /rasp")

bot.polling()
