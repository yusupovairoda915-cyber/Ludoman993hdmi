from aiogram import Router, types
from aiogram.filters import Command
from database.methods import register_user, get_balance # импорт из твоей папки

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # твоя логика регистрации
    pass

