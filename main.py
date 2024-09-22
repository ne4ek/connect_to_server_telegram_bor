from aiogram import Bot, Dispatcher, Router
from conf import API_TOKEN
import asyncio

bot = Bot(token=API_TOKEN)  
router = Router()

from commands.start import *
from commands.help import *
from commands.add_server import * 
from commands.my_hosts import *



async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
