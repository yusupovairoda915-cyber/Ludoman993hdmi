import os
import json
import firebase_admin
from firebase_admin import credentials, db
from config import config

if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_KEY_PATH")
    if firebase_json and firebase_json.strip().startswith("{"):
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate(config.FIREBASE_KEY_PATH)
        
    firebase_admin.initialize_app(cred, {
        'databaseURL': config.DB_URL
    })

def register_user(user_id: int, username: str):
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
    return db.reference(f'users/{user_id}').get()

def update_balance(user_id: int, amount: int):
    ref = db.reference(f'users/{user_id}')
    data = ref.get()
    if data:
        new_balance = data['balance'] + amount
        ref.update({'balance': new_balance})
        return new_balance
    return None

# --- ИСПРАВЛЕННЫЙ БЛОК ТОПА ---

def get_top_users(limit=10):
    """Получает топ игроков из Realtime Database."""
    ref = db.reference('users')
    users = ref.get()
    if not users:
        return []
    
    # Сортируем словарь пользователей по балансу
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('balance', 0), reverse=True)
    
    leaderboard = []
    for uid, data in sorted_users[:limit]:
        leaderboard.append({
            'id': uid,
            'name': data.get('username', 'Аноним'),
            'balance': data.get('balance', 0)
        })
    return leaderboard

def get_user_rank(user_id):
    """Считает ранг пользователя в Realtime Database."""
    ref = db.reference('users')
    users = ref.get()
    if not users or str(user_id) not in users:
        return None
    
    user_balance = users[str(user_id)].get('balance', 0)
    
    # Считаем, сколько людей имеют баланс больше
    rank = 1
    for uid, data in users.items():
        if data.get('balance', 0) > user_balance:
            rank += 1
            
    return rank
        
