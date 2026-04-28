import random 
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.methods import register_user, get_user_data, update_balance

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.full_name
    
    # Регистрируем или получаем данные из Firebase
    is_new = register_user(user_id, username)
    data = get_user_data(user_id)
    balance = data.get('balance', 0) # Получаем баланс из словаря
    
    if is_new:
        greeting = f"🎰 Добро пожаловать в Ludoman993, {username}!\nТебе начислен стартовый капитал!"
    else:
        greeting = f"👋 С возвращением, {username}!"

    # Твой новый текст со списком игр
    welcome_text = (
        f"{greeting}\n\n"
        "Добро пожаловать в казино симулятор (внутриигровые деньги не настоящие и никак не связаны с ними)\n\n"
        "**Игры:**\n"
        "🎰 /slots [сумма] — слоты: риск высокий, но и награды тоже!\n"
        "🎲 /dice [сумма] — подбросить кость: это быстро и не так рисково!\n"
        "🎡 /roulette [цвет: black, red, green] [сумма] — классика азартных игр.\n"
        "📈 /crash [сумма] — успей забрать по выгодному коэффициенту!\n\n"
        "**Заработать:**\n"
        "👨‍🍳 /work — посчитай и выдай сдачу клиенту. (+150)\n\n"
        "Новые способы будут скоро...\n\n"
        f"**Ваш баланс:** 💰 `{balance}` монет."
    )
        
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message(Command("free_money"))
async def cmd_free_money(message: types.Message):
    builder = InlineKeyboardBuilder()
    
    # Твой BlockID из Adsgram
    block_id = "28696"
    # Прямая ссылка для вызова Mini App через официального бота Adsgram
    ad_url = f"https://t.me/AdsgramRewardBot?start={block_id}_{message.from_user.id}"
    
    builder.row(types.InlineKeyboardButton(
        text="📺 Посмотреть рекламу (+500 💰)", 
        url=ad_url
    ))

    await message.answer(
        "Закончились деньги? Не беда!\nПосмотри короткую рекламу и получи **500 монет** на счет.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
@router.message(Command("work"))
async def cmd_work(message: types.Message):
    # Генерируем случайную ситуацию на кассе
    price = random.randint(10, 900)  # Цена товара
    cash_given = random.choice([100, 200, 500, 1000]) # Сколько дал клиент
    
    # Если клиент дал меньше, чем стоит товар — пересчитываем
    if cash_given < price:
        cash_given = 1000
        
    correct_change = cash_given - price
    
    # Создаем варианты ответов (один правильный, два ложных)
    options = [correct_change, correct_change + 50, correct_change - 20]
    random.shuffle(options)
    
    builder = InlineKeyboardBuilder()
    for opt in options:
        # В callback_data зашиваем ответ: "work_ответ_правильныйОтвет"
        builder.row(types.InlineKeyboardButton(
            text=f"💰 {opt} монет", 
            callback_data=f"work_{opt}_{correct_change}"
        ))

    await message.answer(
        f"👨‍🍳 **Смена в магазине!**\n\n"
        f"Покупатель взял товар за **{price}** монет.\n"
        f"Он протягивает тебе купюру в **{cash_given}** монет.\n\n"
        f"**Какую сдачу нужно выдать?**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith('work_'))
async def process_work_answer(callback: types.CallbackQuery):

    # Разбираем данные из кнопки
    _, user_answer, correct_answer = callback.data.split('_')
    
    if user_answer == correct_answer:
        reward = 150 # Сколько платим за правильный ответ
        update_balance(callback.from_user.id, reward)
        await callback.message.edit_text(
            f"✅ **Верно!**\nВы быстро отсчитали сдачу и заработали **{reward}** монет.\n"
            f"Теперь можно снова в казино! /casino"
        )
    else:
        await callback.message.edit_text(
            f"❌ **Ошибка!**\nВы обсчитали покупателя, и администратор оштрафовал вас.\n"
            f"Денег не начислено. Попробуй еще раз: /work"
        )
    await callback.answer()
@router.message(Command("top"))
async def cmd_top(message: types.Message):
    user_id = message.from_user.id
    top_list = get_top_users(limit=10)
    user_rank = get_user_rank(user_id)
    
    if not top_list:
        await message.answer("🏆 Список лидеров пока пуст!")
        return

    text = "🏆 **Таблица лидеров Ludoman993**\n\n"
    
    for i, user in enumerate(top_list, 1):
        place = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        
        # Выделяем самого пользователя в общем списке, если он там есть
        name_text = f"**{user['name']}** (ЭТО ВЫ)" if i == user_rank else user['name']
        name = name_text.replace('_', '\\_').replace('*', '\\*')
        
        text += f"{place} {name} — 💰 `{user['balance']}`\n"

    # --- ТВОЯ ОРИГИНАЛЬНАЯ ИДЕЯ: Титулы ---
    title = "💸 Начинающий"
    if user_rank == 1: title = "👑 Бог Азарта"
    elif user_rank <= 3: title = "💎 Элита Юнусабада"
    elif user_rank <= 10: title = "🎰 Хайроллер"
    elif user_rank <= 50: title = "🃏 Игрок"

    text += f"\n" + "—" * 15 + "\n"
    text += f"👤 **Ваше место:** `{user_rank}`\n"
    text += f"🎖 **Ваш титул:** {title}"
    
    await message.answer(text, parse_mode="Markdown")
