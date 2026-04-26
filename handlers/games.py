import asyncio
import random  # Для генерации точки взрыва
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder  # Для создания кнопок
from aiogram.exceptions import TelegramBadRequest  # Чтобы бот не падал при обновлении текста
from database.methods import get_user_data, update_balance

router = Router()


@router.message(Command("slots"))
async def cmd_slots(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    if not user_data:
        return await message.answer("Сначала напиши /start!")

    # Проверяем, ввел ли пользователь сумму ставки
    if not command.args or not command.args.isdigit():
        return await message.answer("Пример: `/slots 100`", parse_mode="Markdown")

    bet = int(command.args)
    current_balance = user_data['balance']

    if bet <= 0:
        return await message.answer("Ставка должна быть больше 0!")
    
    if bet > current_balance:
        return await message.answer(f"Недостаточно средств! Твой баланс: {current_balance} 💰")

    # Списываем ставку сразу
    update_balance(user_id, -bet)

    # Крутим барабан
    msg = await message.answer_dice(emoji="🎰")
    
    # Ждем, пока анимация закончится (около 2 секунд)
    await asyncio.sleep(2)

    # Логика выигрыша (значения от 1 до 64)
    # 1, 22, 43, 64 — это комбинации из трех одинаковых символов
    win_value = msg.dice.value
    
    reward = 0
    if win_value == 1:  # Семерки (Джекпот!)
        reward = bet * 10
        result_text = f"💎 ДЖЕКПОТ! Тройные семерки! Выигрыш: {reward} 💰"
    elif win_value in [22, 43, 64]:  # Другие три в ряд
        reward = bet * 5
        result_text = f"🎰 Три в ряд! Хороший улов: {reward} 💰"
    elif win_value in [16, 32, 48]: # Две одинаковых (условно)
        reward = bet * 2
        result_text = f"✨ Неплохо! Выигрыш: {reward} 💰"
    else:
        result_text = "❌ Упс! Повезет в следующий раз. Баланс списан."

    # Если выиграл — начисляем
    if reward > 0:
        new_balance = update_balance(user_id, reward)
        await message.reply(f"{result_text}\nТвой новый баланс: {new_balance} 💰")
    else:
        await message.reply(result_text)
@router.message(Command("dice"))
async def cmd_dice(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    if not user_data:
        return await message.answer("Сначала напиши /start!")

    if not command.args or not command.args.isdigit():
        return await message.answer("Пример: `/dice 100`", parse_mode="Markdown")

    bet = int(command.args)
    current_balance = user_data['balance']

    if bet <= 0:
        return await message.answer("Ставка должна быть больше 0!")
    
    if bet > current_balance:
        return await message.answer(f"Недостаточно средств! Баланс: {current_balance} 💰")

    # Списываем ставку
    update_balance(user_id, -bet)

    # Бросаем обычный кубик
    msg = await message.answer_dice(emoji="🎲")
    value = msg.dice.value
    
    await asyncio.sleep(3) # Ждем анимацию

    if value >= 4: # Победа на 4, 5, 6
        reward = bet * 2
        new_balance = update_balance(user_id, reward)
        await message.reply(f"📈 Выпало {value}! Ты выиграл: {reward} 💰\nБаланс: {new_balance}")
    else:
        await message.reply(f"📉 Выпало {value}. Проигрыш! Попробуй еще раз.")
import random

@router.message(Command("roulette"))
async def cmd_roulette(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    # Проверка команды: /roulette [цвет] [ставка]
    args = command.args.split() if command.args else []
    if len(args) < 2:
        return await message.answer("Пример: `/roulette red 100` (цвета: red, black, zero)", parse_mode="Markdown")

    choice = args[0].lower()
    bet = int(args[1])
    
    if choice not in ['red', 'black', 'zero']:
        return await message.answer("Выбери: red, black или zero!")

    if bet > user_data['balance']:
        return await message.answer("Денег нет, но вы держитесь!")

    update_balance(user_id, -bet)

    # Анимация крутки (можно просто текстом или гифкой)
    msg = await message.answer("🎰 Шарик запущен...")
    await asyncio.sleep(2)

    # Генерируем результат (0-36)
    # 0 - зеро, остальные пополам red/black
    result_number = random.randint(0, 36)
    
    if result_number == 0:
        win_color = 'zero'
    elif result_number % 2 == 0:
        win_color = 'black'
    else:
        win_color = 'red'

    if choice == win_color:
        # На зеро множитель x35, на цвета x2
        multiplier = 35 if win_color == 'zero' else 2
        reward = bet * multiplier
        new_balance = update_balance(user_id, reward)
        await msg.edit_text(f"Выпало: {result_number} ({win_color})! 🎉\nТы выиграл: {reward} 💰\nБаланс: {new_balance}")
    else:
        await msg.edit_text(f"Выпало: {result_number} ({win_color}). 💀\nСтавка проиграна!")
# В начало файла к импортам добавь:
# current_games = {} 

active_crashes = set() # Список ID игроков, которые сейчас в полете

@router.message(Command("crash"))
async def cmd_crash(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    
    if user_id in active_crashes:
        return await message.answer("У тебя уже летит одна ракета! Дождись финиша.")

    user_data = get_user_data(user_id)
    if not command.args or not command.args.isdigit():
        return await message.answer("🚀 Пример: `/crash 100`")

    bet = int(command.args)
    if bet > user_data['balance'] or bet <= 0:
        return await message.answer("Недостаточно монет!")

    update_balance(user_id, -bet)
    active_crashes.add(user_id) # ПОМЕЧАЕМ, ЧТО ИГРОК В ИГРЕ

    crash_point = 1.0 if random.random() < 0.1 else round(random.uniform(1.1, 10.0), 2)
    current_multiplier = 1.0
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"💰 ЗАБРАТЬ (1.0x)", callback_data=f"cr_{user_id}_{bet}_{crash_point}")
    
    game_msg = await message.answer(
        f"🚀 **РАКЕТА ПОШЛА!**\n\n📈 Множитель: **{current_multiplier}x**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

    while current_multiplier < crash_point:
        await asyncio.sleep(0.8)
        
        # ПРОВЕРКА: Если игрока больше нет в списке active_crashes, значит он нажал "ЗАБРАТЬ"
        if user_id not in active_crashes:
            return # ПРОСТО ВЫХОДИМ ИЗ ФУНКЦИИ, ЦИКЛ УМИРАЕТ

        current_multiplier = round(current_multiplier + 0.1, 2)
        
        if current_multiplier >= crash_point:
            break

        new_kb = InlineKeyboardBuilder()
        new_kb.button(text=f"💰 ЗАБРАТЬ ({current_multiplier}x)", callback_data=f"cr_{user_id}_{bet}_{crash_point}")
        
        try:
            await game_msg.edit_text(
                f"🚀 **ЛЕЙТИИИМ!**\n\n📈 Множитель: **{current_multiplier}x**\n💰 Куш: {int(bet * current_multiplier)}",
                reply_markup=new_kb.as_markup(),
                parse_mode="Markdown"
            )
        except:
            continue

    # Если долетели до краша и не вышли из функции раньше
    if user_id in active_crashes:
        active_crashes.remove(user_id)
        await game_msg.edit_text(f"💥 **БА-БАХ!**\n\nВзрыв на **{crash_point}x**.\nМинус {bet} 💰")

@router.callback_query(F.data.startswith("cr_"))
async def crash_callback(callback: types.CallbackQuery):
    data = callback.data.split("_")
    u_id, bet, limit = int(data[1]), int(data[2]), float(data[3])
    
    if callback.from_user.id != u_id:
        return await callback.answer("Это не твоя ракета!", show_alert=True)

    if u_id not in active_crashes:
        return await callback.answer("Игра уже закончена!")

    try:
        cur_m = float(callback.message.text.split("Множитель: ")[1].split("x")[0])
    except:
        return

    if cur_m < limit:
        # ПЕРВЫМ ДЕЛОМ УДАЛЯЕМ ИЗ АКТИВНЫХ (это остановит цикл в cmd_crash)
        active_crashes.remove(u_id)
        
        reward = int(bet * cur_m)
        update_balance(u_id, reward)
        
        await callback.message.edit_text(f"✅ **УСПЕЛ!**\n\nЗабрал на: **{cur_m}x**\nВыигрыш: **{reward} 💰**")
        await callback.answer("Баланс пополнен!")
    else:
        await callback.answer("Бум! Поздно!", show_alert=True)

    # Если ракета долетела до взрыва и цикл не прервался return-ом
    await game_msg.edit_text(f"💥 **БА-БАХ!**\n\nВзрыв на **{crash_point}x**.\nМинус {bet} 💰")

@router.callback_query(F.data.startswith("cr_"))
async def crash_callback(callback: types.CallbackQuery):
    data = callback.data.split("_")
    bet = int(data[1])
    crash_limit = float(data[2])
    
    # Достаем текущий икс из текста
    try:
        cur_m = float(callback.message.text.split("Множитель: ")[1].split("x")[0])
    except:
        return

    if cur_m < crash_limit:
        reward = int(bet * cur_m)
        update_balance(callback.from_user.id, reward)
        # МЕНЯЕМ ТЕКСТ И УДАЛЯЕМ КНОПКИ (это остановит цикл while)
        await callback.message.edit_text(f"✅ **УСПЕЛ!**\n\nЗабрал на: **{cur_m}x**\nВыигрыш: **{reward} 💰**")
        await callback.answer("Баланс пополнен!")
    else:
        await callback.answer("Слишком поздно!", show_alert=True)

from aiogram.utils.keyboard import InlineKeyboardBuilder

@router.message(Command("free_money"))
async def show_ads(message: types.Message):
    user_id = message.from_user.id
    # Твой ID из кабинета
    block_id = "28696" 
    
    # Ссылка на рекламу
    ad_url = f"https://render.adsgram.ai/show?blockId={block_id}&userId={user_id}"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Посмотреть рекламу", url=ad_url)
    
    await message.answer(
        "💰 **Нужны монеты?**\nПосмотри короткое видео и получишь **500 монет** на баланс!",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
