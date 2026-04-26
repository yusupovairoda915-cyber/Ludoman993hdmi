import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers import users  # Импортируем наш будущий модуль с хендлерами

# Настраиваем логирование, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализируем бота и диспетчер
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем роутеры (маршруты) из папки handlers
    dp.include_router(users.router)

    # Запускаем бота (пропускаем накопленные сообщения)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")

