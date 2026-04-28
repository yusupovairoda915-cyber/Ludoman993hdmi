import os
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.methods import (
    get_user_data, update_balance, get_top_users,
    get_user_by_username, get_all_users
)

router = Router()

# ID админа
ADMIN_ID = os.environ.get("ADMIN_ID", "7268169826")  # @prosto_993 Telegram ID

def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    return str(user_id) == str(ADMIN_ID)

# ============ АДМИН КОМАНДЫ ============

@router.message(Command("admin"))
async def cmd_admin_menu(message: types.Message):
    """Меню админа"""
    if not is_admin(message.from_user.id):
        return await message.answer("❌ У вас нет доступа к админ команде!")
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Изменить баланс пользователю", callback_data="admin_change_balance")
    builder.button(text="📢 Отправить сообщение всем", callback_data="admin_broadcast")
    builder.button(text="👥 Статистика", callback_data="admin_stats")
    builder.adjust(1)
    
    await message.answer(
        "🔐 **Админ-панель**\n\n"
        "Выберите действие:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_change_balance")
async def change_balance_start(callback: types.CallbackQuery):
    """Начинаем процесс изменения баланса"""
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Доступ запрещен!", show_alert=True)
    
    await callback.message.edit_text(
        "💰 **Изменение баланса**\n\n"
        "Введите юзернейм пользователя:\n\n"
        "_Напиши_: `username`",
        parse_mode="Markdown"
    )
    # Сохраняем состояние (простой способ - через callback_data в следующем шаге)
    await callback.answer()

@router.message(Command("balance_admin"))
async def cmd_balance_admin(message: types.Message, command: CommandObject):
    """Команда: /balance_admin username 500
    Устанавливает баланс пользователю на конкретную сумму"""
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Доступ запрещен!")
    
    args = command.args.split() if command.args else []
    if len(args) < 2:
        return await message.answer(
            "❌ Использование: `/balance_admin username сумма`\n\n"
            "_Примеры:_\n"
            "`/balance_admin prosto_993 5000` — установить баланс 5000\n"
            "`/balance_admin john_doe +1000` — добавить 1000\n"
            "`/balance_admin alice_smith -500` — отнять 500",
            parse_mode="Markdown"
        )
    
    username = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        return await message.answer("❌ Сумма должна быть числом!")
    
    # Ищем пользователя по юзернейму
    user_id = get_user_by_username(username)
    if not user_id:
        return await message.answer(f"❌ Пользователь `{username}` не найден!", parse_mode="Markdown")
    
    # Если число с + или -, то добавляем/отнимаем, иначе устанавливаем
    if str(amount).startswith('+') or str(amount).startswith('-'):
        new_balance = update_balance(user_id, amount)
        action = "добавлено" if amount > 0 else "отнято"
        await message.answer(
            f"✅ {abs(amount)} монет {action} пользователю `{username}`\n"
            f"Новый баланс: **{new_balance} 💰**",
            parse_mode="Markdown"
        )
    else:
        # Устанавливаем конкретное значение
        current_data = get_user_data(user_id)
        current_balance = current_data.get('balance', 0)
        diff = amount - current_balance
        update_balance(user_id, diff)
        
        await message.answer(
            f"✅ Баланс пользователя `{username}` установлен на **{amount} 💰**",
            parse_mode="Markdown"
        )

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, command: CommandObject):
    """Отправляет сообщение всем пользователям
    Использование: /broadcast Ваше сообщение тут"""
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Доступ запрещен!")
    
    if not command.args:
        return await message.answer(
            "❌ Использование: `/broadcast Ваше сообщение`",
            parse_mode="Markdown"
        )
    
    broadcast_text = command.args
    
    # Получаем всех пользователей
    all_users = get_all_users()
    
    if not all_users:
        return await message.answer("❌ Нет пользователей для отправки!")
    
    # Отправляем сообщение
    from bot import bot
    
    success = 0
    failed = 0
    
    await message.answer(
        f"📢 **Начало рассылки...**\n"
        f"Получателей: {len(all_users)}"
    )
    
    for user_id in all_users:
        try:
            await bot.send_message(
                user_id,
                f"📢 **Объявление от администратора:**\n\n{broadcast_text}",
                parse_mode="Markdown"
            )
            success += 1
        except Exception as e:
            failed += 1
            print(f"Ошибка отправки {user_id}: {e}")
    
    await message.answer(
        f"✅ **Рассылка завершена!**\n\n"
        f"✔️ Отправлено: {success}\n"
        f"❌ Ошибок: {failed}",
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_broadcast")
async def broadcast_callback(callback: types.CallbackQuery):
    """Обработчик кнопки рассылки"""
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Доступ запрещен!", show_alert=True)
    
    await callback.message.edit_text(
        "📢 **Рассылка сообщения**\n\n"
        "Используйте команду:\n"
        "`/broadcast Ваше сообщение`\n\n"
        "_Пример:_\n"
        "`/broadcast 🎉 Поздравляем с обновлением! Новые игры добавлены!`",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    """Статистика по игроку"""
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ Доступ запрещен!", show_alert=True)
    
    top_users = get_top_users(limit=5)
    total_users = len(get_all_users())
    
    text = f"👥 **Статистика**\n\n"
    text += f"Всего пользователей: {total_users}\n\n"
    text += "🏆 **Топ 5 игроков:**\n"
    
    for i, user in enumerate(top_users, 1):
        text += f"{i}. {user['name']} — {user['balance']} 💰\n"
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

# ============ ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ ============

@router.message(Command("my_id"))
async def cmd_my_id(message: types.Message):
    """Показывает ваш Telegram ID"""
    await message.answer(
        f"🆔 **Ваш Telegram ID:**\n`{message.from_user.id}`",
        parse_mode="Markdown"
    )
