from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.methods import get_user_data, update_balance, get_all_users
from config import config

router = Router()

# Функция для проверки, является ли пользователь админом
async def is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID

# ========== КОМАНДА /admin ==========
@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Главное меню админа"""
    if not await is_admin(message.from_user.id):
        await message.answer("❌ У тебя нет доступа к админ-функциям!")
        return
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="💰 Изменить баланс", 
        callback_data="admin_balance"
    ))
    builder.row(types.InlineKeyboardButton(
        text="📢 Отправить сообщение", 
        callback_data="admin_broadcast"
    ))
    builder.row(types.InlineKeyboardButton(
        text="📊 Статистика", 
        callback_data="admin_stats"
    ))
    
    await message.answer(
        "🔐 **Админ-панель**\n\n"
        "Выбери действие:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

# ========== ИЗМЕНЕНИЕ БАЛАНСА ==========
@router.callback_query(F.data == "admin_balance")
async def admin_balance_menu(callback: types.CallbackQuery):
    """Меню изменения баланса"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "💰 **Изменение баланса**\n\n"
        "Отправь сообщение в формате:\n"
        "`/set_balance [user_id] [количество]`\n\n"
        "Пример: `/set_balance 123456789 5000`\n"
        "(Можно указать отрицательное число для вычитания)",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("set_balance"))
async def cmd_set_balance(message: types.Message, command: CommandObject):
    """Установить баланс пользователю"""
    if not await is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён!")
        return
    
    if not command.args:
        await message.answer(
            "Использование: `/set_balance [user_id] [сумма]`\n"
            "Пример: `/set_balance 123456789 5000`",
            parse_mode="Markdown"
        )
        return
    
    args = command.args.split()
    if len(args) < 2:
        await message.answer("❌ Не хватает аргументов!")
        return
    
    try:
        user_id = int(args[0])
        amount = int(args[1])
    except ValueError:
        await message.answer("❌ ID и сумма должны быть числами!")
        return
    
    # Проверяем, существует ли пользователь
    user_data = get_user_data(user_id)
    if not user_data:
        await message.answer(f"❌ Пользователь с ID {user_id} не найден!")
        return
    
    # Обновляем баланс
    new_balance = update_balance(user_id, amount)
    
    await message.answer(
        f"✅ **Баланс обновлён!**\n\n"
        f"👤 ID: `{user_id}`\n"
        f"💰 Сумма: `{amount}`\n"
        f"💵 Новый баланс: `{new_balance}`",
        parse_mode="Markdown"
    )

# ========== МАССОВАЯ РАССЫЛКА ==========
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_menu(callback: types.CallbackQuery):
    """Меню рассылки"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 **Отправить сообщение всем**\n\n"
        "Отправь сообщение в формате:\n"
        "`/broadcast [текст]`\n\n"
        "Пример:\n"
        "`/broadcast 🎉 Новое обновление! Проверьте игры!`",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, command: CommandObject):
    """Отправить сообщение всем пользователям"""
    if not await is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён!")
        return
    
    if not command.args:
        await message.answer("❌ Укажи текст сообщения!")
        return
    
    broadcast_text = command.args
    
    # Получаем всех пользователей
    all_users = get_all_users()
    
    if not all_users:
        await message.answer("❌ Пользователи не найдены!")
        return
    
    # Отправляем сообщение каждому пользователю
    success_count = 0
    error_count = 0
    
    # Получаем бота из контекста
    bot = message.bot
    
    for user_id in all_users:
        try:
            await bot.send_message(
                user_id,
                f"📢 **Объявление от администратора:**\n\n{broadcast_text}",
                parse_mode="Markdown"
            )
            success_count += 1
        except Exception as e:
            error_count += 1
            print(f"Ошибка отправки для {user_id}: {e}")
    
    await message.answer(
        f"✅ **Рассылка завершена!**\n\n"
        f"✉️ Доставлено: `{success_count}`\n"
        f"❌ Ошибок: `{error_count}`",
        parse_mode="Markdown"
    )

# ========== СТАТИСТИКА ==========
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    """Показать статистику"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещён!", show_alert=True)
        return
    
    all_users = get_all_users()
    
    if not all_users:
        await callback.message.edit_text("📊 Пользователи не найдены!")
        await callback.answer()
        return
    
    # Считаем статистику
    total_users = len(all_users)
    total_balance = 0
    
    for user_id in all_users:
        user_data = get_user_data(user_id)
        if user_data:
            total_balance += user_data.get('balance', 0)
    
    avg_balance = total_balance // total_users if total_users > 0 else 0
    
    await callback.message.edit_text(
        f"📊 **Статистика бота**\n\n"
        f"👥 Всего пользователей: `{total_users}`\n"
        f"💰 Общий баланс: `{total_balance}`\n"
        f"📈 Средний баланс: `{avg_balance}`",
        parse_mode="Markdown"
    )
    await callback.answer()
