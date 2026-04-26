import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
# 1. Добавь сюда импорт games через запятую
from handlers import users, games  

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # 2. И здесь обязательно зарегистрируй роутер для игр
    dp.include_router(users.router)
    dp.include_router(games.router) 

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
