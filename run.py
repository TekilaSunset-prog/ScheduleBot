import asyncio
import logging

from aiogram import Dispatcher, Bot

from jsons.jsfiles import get_param
from handlers.scheduler import router

logging.basicConfig(level=logging.INFO)
bot = Bot(token=get_param('Token'))
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
