import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
import config  # Твой файл конфига
from handlers import users, games
from database.firebase_storage import update_balance

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота. Пробуем взять из Railway, если нет - из config.py
TOKEN = os.environ.get("BOT_TOKEN") or config.BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ОБРАБОТЧИК РЕКЛАМЫ (СЕРВЕР) ---
async def handle_adsgram_reward(request):
    user_id = request.query.get("user_id")
    if user_id:
        try:
            # Начисляем монеты
            await update_balance(int(user_id), 500)
            # Отправляем сообщение в ТГ
            await bot.send_message(user_id, "💎 Награда: +500 монет за просмотр рекламы!")
        except Exception as e:
            logging.error(f"Ошибка начисления: {e}")
    return web.Response(text="ok")

async def main():
    # Настраиваем сервер для Railway на порту 8080
    app = web.Application()
    app.router.add_get('/ads_reward', handle_adsgram_reward)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Порт 8080 - тот самый, который ты указал в Networking
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Adsgram server started on port {port}")

    # Подключаем твои роутеры
    dp.include_router(users.router)
    dp.include_router(games.router)

    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
