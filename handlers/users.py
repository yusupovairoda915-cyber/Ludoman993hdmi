from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.methods import register_user, get_user_data

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
