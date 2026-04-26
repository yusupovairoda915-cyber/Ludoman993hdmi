import os
import json
import firebase_admin
from firebase_admin import credentials, db
from config import config

# Проверяем, не инициализировано ли приложение ранее
if not firebase_admin._apps:
    # Пытаемся взять данные из переменной Railway
    firebase_json = os.getenv("FIREBASE_KEY_PATH")

    # Проверяем: если в переменной лежит JSON-текст (начинается с {), парсим его
    if firebase_json and firebase_json.strip().startswith("{"):
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
    else:
        # Если переменной нет или там просто путь, используем старый метод (для локалки)
        cred = credentials.Certificate(config.FIREBASE_KEY_PATH)
        
    firebase_admin.initialize_app(cred, {
        'databaseURL': config.DB_URL
    })


def register_user(user_id: int, username: str):
    """Регистрирует новичка в базе и выдает стартовый капитал."""
    ref = db.reference(f'users/{user_id}')
    user_data = ref.get()
    
    if user_data is None:
        ref.set({
            'username': username,
            'balance': 1000,
            'wins': 0,
            'losses': 0
        })
        return True
    return False

def get_user_data(user_id: int):
    """Получает всю инфу о лудомане (баланс, стата)."""
    return db.reference(f'users/{user_id}').get()

def update_balance(user_id: int, amount: int):
    """
    Универсальная функция: 
    Если amount > 0 — это выигрыш.
    Если amount < 0 — это ставка (минус из баланса).
    """
    ref = db.reference(f'users/{user_id}')
    data = ref.get()
    
    if data:
        new_balance = data['balance'] + amount
        ref.update({'balance': new_balance})
        return new_balance
    return None

def get_leaderboard(limit: int = 5):
    """Метод для 'доски почета' (топ богачей)."""
    ref = db.reference('users')
    # Firebase умеет в сортировку, но для малых баз проще сделать так:
    users = ref.get()
    if not users:
        return []
    
    # Сортируем по балансу и берем топ
    sorted_users = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)
    return sorted_users[:limit]

