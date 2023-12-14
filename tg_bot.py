import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import logging
import sys



from config import Settings
from tg_bot_backend.handlers import router

class TGBot:
    '''Клас ТГ бота'''
    def __init__(self, Settings: str = Settings):
        self.settings = Settings()
        self.bot = Bot(self.settings.BOT_TOKEN, parse_mode=ParseMode.HTML )
        self.tg_dispatcher = Dispatcher()
        self.tg_dispatcher.include_router(router)

    async def start(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        await self.tg_dispatcher.start_polling(self.bot, skip_updates=True)

async def main():

    bot = TGBot()
    await bot.start()



if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())