import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN  # Используем твой конфиг
from handlers import users, games
from database.firebase_storage import update_balance

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- СЕКЦИЯ ADSGRAM (WEBHOOK) ---

async def handle_adsgram_reward(request):
    user_id = request.query.get("user_id")
    
    if user_id:
        try:
            user_id_int = int(user_id)
            reward_amount = 500
            
            # Начисляем монеты в Firebase
            await update_balance(user_id_int, reward_amount)
            
            # Уведомляем пользователя
            await bot.send_message(
                user_id_int, 
                f"💎 **Награда получена!**\nВы посмотрели рекламу и получили {reward_amount} монет.",
                parse_mode="Markdown"
            )
            logging.info(f"Reward sent to user {user_id}")
        except Exception as e:
            logging.error(f"Error in ads callback: {e}")
            
    return web.Response(text="ok")

# --- ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА ---

async def main():
    # 1. Настраиваем и запускаем веб-сервер для приема наград
    app = web.Application()
    app.router.add_get('/ads_reward', handle_adsgram_reward)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Railway сам подставит нужный порт в переменную PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Adsgram Webhook server started on port {port}")

    # 2. Регистрация роутеров (как у тебя и было)
    dp.include_router(users.router)
    dp.include_router(games.router)

    # 3. Очистка очереди обновлений и запуск пуллинга
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__
