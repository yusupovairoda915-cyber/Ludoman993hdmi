import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

class Config:
    # Токен бота из BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Ссылка на Realtime Database (из консоли Firebase)
    DB_URL = os.getenv("DB_URL")
    
    # Путь к твоему JSON-файлу с ключами (паспорт Firebase)
    FIREBASE_KEY_PATH = "serviceAccountKey.json"
    
    # ID администратора (замени на ID @prosto_993)
    ADMIN_ID = 123456789  # ЗАМЕНИ НА РЕАЛЬНЫЙ ID!

# Экземпляр конфига для удобного импорта
config = Config()
