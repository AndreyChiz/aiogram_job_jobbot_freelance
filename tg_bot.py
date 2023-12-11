import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import logging
import sys


from config import Settings
from tg_bot_backend.handlers import router

dp = Dispatcher()
dp.include_router(router)

async def main():
    bot = Bot(Settings().BOT_TOKEN, parse_mode=ParseMode.HTML, )
    await dp.start_polling(bot, skip_updates=True)



if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())