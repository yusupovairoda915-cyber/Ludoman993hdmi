import random 
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.methods import register_user, get_user_data, update_balance
from aiogram import Router, types, F


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.full_name
    
    # Регистрируем в Firebase
    is_new = register_user(user_id, username)
    data = get_user_data(user_id)
    
    if is_new:
        welcome_text = (
            f"🎰 Добро пожаловать в Ludoman993, {username}!\n\n"
            f"Тебе начислен стартовый капитал: 💰 **{data['balance']}** монет.\n"
            f"Используй /casino чтобы испытать удачу!"
        )
    else:
        welcome_text = (
            f"👋 С возвращением, элита гемблинга, {username}!\n"
            f"Твой баланс: 💰 **{data['balance']}** монет."
        )
        
    await message.answer(welcome_text, parse_mode="Markdown")

@router.message(Command("balance"))
async def cmd_balance(message: types.Message):
    data = get_user_data(message.from_user.id)
    if data:
        await message.answer(f"💵 Ваш текущий баланс: **{data['balance']}** монет.", parse_mode="Markdown")
    else:
        await message.answer("Сначала напиши /start, чтобы открыть счет!")

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
        await update_balance(callback.from_user.id, reward)
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
