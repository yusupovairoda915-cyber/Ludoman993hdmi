import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from handlers import users, games
from database.firebase_storage import update_balance

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ПОЛУЧАЕМ ТОКЕН ИЗ ПЕРЕМЕННЫХ RAILWAY
# Если Railway не найдет переменную, он выдаст ошибку, которую мы увидим в логах
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logging.error("BOT_TOKEN not found in environment variables!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- СЕКЦИЯ ADSGRAM (WEBHOOK) ---

async def handle_adsgram_reward(request):
    user_id = request.query.get("user_id")
    logging.info(f"Received callback from Adsgram for user: {user_id}")
    
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
            logging.info(f"Successfully rewarded user {user_id}")
        except Exception as e:
            logging.error(f"Error processing reward for user {user_id}: {e}")
            
    return web.Response(text="ok")

# --- ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА ---

async def main():
    # 1. Запуск веб-сервера (порт 8080 по умолчанию для Railway)
    app = web.Application()
    app.router.add_get('/ads_reward', handle_adsgram_reward)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"🚀 Adsgram server is listening on port {port}")

    # 2. Регистрация роутеров
    dp.include_router(users.router)
    dp.include_router(games.router)

    # 3. Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
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
