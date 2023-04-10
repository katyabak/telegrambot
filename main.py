from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes,CallbackContext, CallbackQueryHandler
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json
import random
import time

# Инициализация логгера
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Чтение токена бота из файла конфигурации
with open('config.txt', 'r') as f:
    TOKEN = f.read().strip()
# создание updater
updater = Application.builder().token(TOKEN).build()
# флаг, отвечающий за состояние бота
bot_active = True

# Функция-обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_active
    logger.info("Пользователь %s начал диалог.", update.effective_user.first_name)
    if not bot_active:
        bot_active = True
        text = "Бот снова активен. Нажми на кнопку ниже чтобы узнать доступные команды."
        keyboard = [[InlineKeyboardButton("Доступные команды", callback_data="Доступные команды")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_html(text, reply_markup=reply_markup)
    else:
        text = rf"Привет, {update.effective_user.mention_html()}! Я бот. Нажми на кнопку ниже чтобы узнать доступные команды."
        keyboard = [[InlineKeyboardButton("Доступные команды", callback_data="Доступные команды")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_html(text, reply_markup=reply_markup)

# Функция-обработчик меню
async def menu(update: Update, context: CallbackContext) -> None:
    global bot_active
    if bot_active:
        query = update.callback_query
        await query.answer()
        if query.data == "Доступные команды":
            await query.message.reply_text("Список доступных команд:\n"
                        "/help - список доступных команд\n"
                        "/echo <текст> - эхо-ответ с переданным текстом\n"
                        "/weather <город> - вывод текущей погоды в указанном городе\n"
                        "/news - вывод последних новостей\n"
                        "/joke - вывод случайной шутки\n"
                        "/stop - прощание с пользователем и остановка работы бота")
        else:
            await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

# Функция-обработчик команды /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_active
    if bot_active:
        logger.info("Пользователь %s открыл /help.", update.effective_user.first_name)
        await update.message.reply_text("Список доступных команд:\n"
                        "/help - список доступных команд\n"
                        "/echo <текст> - эхо-ответ с переданным текстом\n"
                        "/weather <город> - вывод текущей погоды в указанном городе\n"
                        "/news - вывод последних новостей\n"
                        "/joke - вывод случайной шутки\n"
                        "/stop - прощание с пользователем и остановка работы бота")
    else:
        logger.info("Пользователю %s не удалось открыть /help.", update.effective_user.first_name)
        await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

# Функция-обработчик команды /echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_active
    if bot_active:
        logger.info("Пользователь %s выполнил /echo.", update.effective_user.first_name)
        await update.message.reply_text(update.message.text.split(' ', 1)[1])
    else:
        logger.info("Пользователю %s не удалось выполнить /echo.", update.effective_user.first_name)
        await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

# функция /weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_active
    if bot_active:
        logger.info("Пользователь %s выполнил /weather.", update.effective_user.first_name)
        # Получаем название города из аргумента команды
        city = context.args[0]
        # Формируем запрос к API OpenWeatherMap
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=63fbcc00cf500cddf08641995ee9c4a0&units=metric&lang=ru"
        response = requests.get(url)
        data = json.loads(response.text)
        # Обрабатываем ответ API
        if data["cod"] != "404":
            weather_info = data["weather"][0]
            main_info = data["main"]
            wind_info = data["wind"]
            city_name = data["name"]
            country = data["sys"]["country"]
            # Формируем сообщение о погоде и отправляем пользователю
            message = f"Погода в городе {city_name}, {country}:\n" \
                    f"{weather_info['description'].capitalize()}\n" \
                    f"Температура: {main_info['temp']}°C\n" \
                    f"Ощущается как: {main_info['feels_like']}°C\n" \
                    f"Минимальная температура: {main_info['temp_min']}°C\n" \
                    f"Максимальная температура: {main_info['temp_max']}°C\n" \
                    f"Ветер: {wind_info['speed']} м/c\n"
            await update.message.reply_text(message)
        else:
            # Если город не найден, отправляем соответствующее сообщение
            await update.message.reply_text("Город не найден. Введите название еще раз.")
    else:
        logger.info("Пользователю %s не удалось выполнить /weather.", update.effective_user.first_name)
        await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

# Функция-обработчик команды /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_active
    if bot_active:
        logger.info("Пользователь %s выполнил /news.", update.effective_user.first_name)
        api_key = '514446dd8dda4a8f99d5b5cc3bf0dc39'
        url = f'https://newsapi.org/v2/top-headlines?country=ru&apiKey={api_key}'
        # отправляем запрос и получаем ответ в формате json
        response = requests.get(url)
        news = response.json()['articles']
        # выводим заголовки новостей
        news_text = 'Последние новости:\n\n'
        for i, article in enumerate(news):
            news_text += f"{i+1}. {article['title']}\n\n"
        await update.message.reply_text(news_text)
    else:
        logger.info("Пользователю %s не удалось выполнить /news.", update.effective_user.first_name)
        await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

# Функция-обработчик команды /joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_active
    if bot_active:
        logger.info("Пользователь %s выполнил /joke.", update.effective_user.first_name)
        # читаем файл со списком шуток
        with open('jokes.txt', 'r', encoding='utf-8') as f:
            jokes = f.readlines()
        # выбираем случайную шутку из списка
        random_joke = random.choice(jokes)
        # отправляем шутку пользователю
        await update.message.reply_text(random_joke)
    else:
        logger.info("Пользователю %s не удалось выполнить /joke.", update.effective_user.first_name)
        await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Пользователь %s ввел неизвестную команду.", update.effective_user.first_name)
    global bot_active
    if bot_active:
        await update.message.reply_text("Извините, я вас не понял. Введите /help чтобы посмотреть доступные команды.")
    else:
        await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

# errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Произошла ошибка")
    await update.message.reply_text('Ошибка.')

# Функция-обработчик команды /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Пользователь %s завершил работу бота.", update.effective_user.first_name)
    global bot_active
    if bot_active:
        bot_active = False
        await update.message.reply_text("Вы завершили работу бота. Напишите /start для активации бота.")
    else:
        await update.message.reply_text("Бот остановлен. Напишите /start чтобы запустить его.")

def start_bot():
    # добавляем обработчики команд
    updater.add_handler(CommandHandler("start", start))
    updater.add_handler(CallbackQueryHandler(menu))
    updater.add_handler(CommandHandler("help", help))
    updater.add_handler(CommandHandler("echo", echo))
    updater.add_handler(CommandHandler("weather", weather))
    updater.add_handler(CommandHandler("news", news))
    updater.add_handler(CommandHandler("joke", joke))
    updater.add_handler(CommandHandler("stop", stop))
    updater.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    updater.add_error_handler(error)
    # запуск бота в цикле
    while True:
        if bot_active:
            updater.run_polling()
            updater.idle()
        else:
            time.sleep(1)
# запуск бота
if __name__ == '__main__':
    start_bot()