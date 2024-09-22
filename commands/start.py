from aiogram.filters import Command
from aiogram.types import Message
from main import router
from scripts.bd_connections import regist_tg_user


@router.message(Command("start"))
async def telegram_user_registration(message: Message):
    try:     
        registed_user = regist_tg_user(message.from_user)
    except Exception as e:
        raise e
    else:
        print(f"User was registed with {registed_user}")
        await message.answer(f"User was registed with {registed_user}")