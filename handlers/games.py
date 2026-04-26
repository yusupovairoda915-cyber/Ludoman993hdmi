import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
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

