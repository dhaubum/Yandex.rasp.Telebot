# Yandex.rasp.Telebot
Telegram bot for obtaining Yandex schedule.

The data is provided by the service / Данные предоставлены сервисом [Яндекс.Расписания](http://rasp.yandex.ru/)

Using
-----------
Specify your telegram bot token and yandex.rasp API
```
bot = telebot.TeleBot('TOKEN-TelegramBot')
API = ('API-yandex.rasp')
```

Functions
-----------
The Telegram bot provides information about the flight number, the origin location, the departure date and time, the destination location, the arrival time, and the duration of the trip, as well as any stops made during the journey.

What does it look like:
```
Номер рейса: 047А
Отправление: Санкт-Петербург (Московский вокзал)
Дата отправления: 2024-03-31
Время отправления: 17:45
Прибытие: Нижний Новгород (Московский вокзал)
Время прибытия: 16:18
Продолжительность: 1353.0 минут
Остановки: 
```
Questions
-----------
**Where can I get a token for a telegram bot?**

Telegram: Contact [@BotFather](https://t.me/BotFather)

**Where can I get the yandex.rasp API?**

Official website: [yandex.rasp](https://yandex.ru/dev/rasp/raspapi/?ysclid=luec890m9i562783119)

**Why is it so weirdly done?**

I do not know
