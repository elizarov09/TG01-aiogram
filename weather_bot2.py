import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
import requests

API_TOKEN = '7055051091:AAE8zmUdXdAqRUs9dRJZa4B1xZzRNp6Fkh4'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Словарь для хранения городов пользователей
user_cities = {}

class Form(StatesGroup):
    cities = State()

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.set_state(Form.cities)
    await message.reply("Привет! Введите название вашего города или городов через запятую:")

@dp.message(Command("w"))
async def show_weather(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_cities:
        cities = user_cities[user_id]
        weather_data = get_weather_data(cities)
        await message.reply(weather_data)
    else:
        await message.reply("Вы еще не ввели свои города. Используйте /start для ввода.")

@dp.message(Form.cities)
async def save_cities(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cities = message.text.split(',')
    user_cities[user_id] = [city.strip() for city in cities]
    await state.clear()
    await message.reply(f"Города сохранены: {', '.join(user_cities[user_id])}")

def get_coordinates(city):
    try:
        url = f'https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = data[0]['lat']
                lon = data[0]['lon']
                return lat, lon
            else:
                logging.error(f"Невозможно получить данные для города: {city}. Ответ пуст.")
                return None, None
        else:
            logging.error(f"Ошибка при запросе к Nominatim для города {city}. Статус код: {response.status_code}")
            return None, None
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении координат для {city}: {e}")
        return None, None
    except ValueError as ve:
        logging.error(f"Ошибка обработки JSON для {city}: {ve}")
        return None, None

def get_wind_direction(degree):
    if degree >= 348.75 or degree < 11.25:
        return "Северный (N)"
    elif 11.25 <= degree < 33.75:
        return "Северо-Северо-Восточный (NNE)"
    elif 33.75 <= degree < 56.25:
        return "Северо-Восточный (NE)"
    elif 56.25 <= degree < 78.75:
        return "Восточно-Северо-Восточный (ENE)"
    elif 78.75 <= degree < 101.25:
        return "Восточный (E)"
    elif 101.25 <= degree < 123.75:
        return "Восточно-Юго-Восточный (ESE)"
    elif 123.75 <= degree < 146.25:
        return "Юго-Восточный (SE)"
    elif 146.25 <= degree < 168.75:
        return "Юго-Юго-Восточный (SSE)"
    elif 168.75 <= degree < 191.25:
        return "Южный (S)"
    elif 191.25 <= degree < 213.75:
        return "Юго-Юго-Западный (SSW)"
    elif 213.75 <= degree < 236.25:
        return "Юго-Западный (SW)"
    elif 236.25 <= degree < 258.75:
        return "Западно-Юго-Западный (WSW)"
    elif 258.75 <= degree < 281.25:
        return "Западный (W)"
    elif 281.25 <= degree < 303.75:
        return "Западно-Северо-Западный (WNW)"
    elif 303.75 <= degree < 326.25:
        return "Северо-Западный (NW)"
    elif 326.25 <= degree < 348.75:
        return "Северо-Северо-Западный (NNW)"
    else:
        return "Неизвестное направление"

def get_weather_description(code):
    weather_descriptions = {
        0: "Ясно",
        1: "В основном ясно",
        2: "Частично облачно",
        3: "Облачно",
        45: "Туман",
        48: "Оседающий туман",
        51: "Легкий дождь",
        53: "Умеренный дождь",
        55: "Сильный дождь",
        56: "Легкий ледяной дождь",
        57: "Сильный ледяной дождь",
        61: "Легкий дождь",
        63: "Умеренный дождь",
        65: "Сильный дождь",
        66: "Ледяной дождь",
        67: "Сильный ледяной дождь",
        71: "Легкий снег",
        73: "Умеренный снег",
        75: "Сильный снег",
        77: "Град",
        80: "Легкий ливень",
        81: "Умеренный ливень",
        82: "Сильный ливень",
        85: "Легкий снежный ливень",
        86: "Сильный снежный ливень",
        95: "Гроза",
        96: "Гроза с легким градом",
        99: "Гроза с сильным градом",
    }
    return weather_descriptions.get(code, "Неизвестный код погоды")

def get_weather_data(cities):
    weather_info = []
    for city in cities:
        lat, lon = get_coordinates(city)
        if lat and lon:
            try:
                url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true'
                response = requests.get(url)
                data = response.json()
                if 'current_weather' in data:
                    weather_data = data['current_weather']
                    weather_details = [f"{city}:"]
                    if 'temperature' in weather_data:
                        weather_details.append(f"Температура: {weather_data['temperature']}°C")
                    if 'windspeed' in weather_data:
                        weather_details.append(f"Скорость ветра: {weather_data['windspeed']} м/с")
                    if 'winddirection' in weather_data:
                        direction = get_wind_direction(weather_data['winddirection'])
                        weather_details.append(f"Направление ветра: {direction}")
                    if 'weathercode' in weather_data:
                        description = get_weather_description(weather_data['weathercode'])
                        weather_details.append(f"Погодные условия: {description}")
                    if 'humidity' in weather_data:
                        weather_details.append(f"Влажность: {weather_data['humidity']}%")
                    if 'pressure' in weather_data:
                        weather_details.append(f"Давление: {weather_data['pressure']} гПа")
                    weather_info.append("\n".join(weather_details))
                else:
                    weather_info.append(f"{city}: Невозможно получить данные о погоде.")
            except requests.RequestException as e:
                weather_info.append(f"{city}: Ошибка при получении данных о погоде. {str(e)}")
        else:
            weather_info.append(f"{city}: Невозможно получить координаты.")
    return "\n".join(weather_info)

if __name__ == '__main__':
    dp.run_polling(bot)
