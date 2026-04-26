import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
import config
from handlers import users, games
# Импортируем именно из твоего файла methods.py
from database.methods import update_balance 

logging.basicConfig(level=logging.INFO)

# Токен из Railway или конфига
TOKEN = os.environ.get("BOT_TOKEN") or config.BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик, который слушает сигналы от Adsgram
async def handle_adsgram_reward(request):
    user_id = request.query.get("user_id")
    logging.info(f"Пришел сигнал награды для: {user_id}")
    
    if user_id:
        try:
            # Начисляем 500 монет
            await update_balance(int(user_id), 500)
            # Уведомляем юзера
            await bot.send_message(user_id, "💎 **Награда зачислена!**\nВы получили 500 монет за просмотр рекламы.")
        except Exception as e:
            logging.error(f"Ошибка начисления: {e}")
            
    return web.Response(text="ok")

async def main():
    # Запуск веб-сервера для получения наград
    app = web.Application()
    app.router.add_get('/ads_reward', handle_adsgram_reward)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Порт для Railway
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"✅ Adsgram server on port {port}")

    # Регистрация хендлеров
    dp.include_router(users.router)
    dp.include_router(games.router)

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
