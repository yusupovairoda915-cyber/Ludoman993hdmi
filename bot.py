import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
import config  # Твой файл конфига
from handlers import users, games
# ИСПРАВЛЕНО: импортируем из твоего файла methods
from database.methods import update_balance 

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота. Берем из Railway или из конфига
TOKEN = os.environ.get("BOT_TOKEN") or config.BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ОБРАБОТЧИК РЕКЛАМЫ (СЕРВЕР) ---
async def handle_adsgram_reward(request):
    user_id = request.query.get("user_id")
    logging.info(f"Запрос от Adsgram для юзера: {user_id}")
    
    if user_id:
        try:
            # Начисляем монеты через твой метод
            await update_balance(int(user_id), 500)
            # Отправляем сообщение в ТГ
            await bot.send_message(user_id, "💎 Награда: +500 монет за просмотр рекламы!")
            logging.info(f"Награда выдана успешно для {user_id}")
        except Exception as e:
            logging.error(f"Ошибка при начислении: {e}")
            
    return web.Response(text="ok")

async def main():
    # Настраиваем веб-сервер для Railway
    app = web.Application()
    app.router.add_get('/ads_reward', handle_adsgram_reward)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Railway использует порт 8080
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🚀 Сервер Adsgram запущен на порту {port}")

    # Подключаем твои роутеры
    dp.include_router(users.router)
    dp.include_router(games.router)

    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот выключен")
