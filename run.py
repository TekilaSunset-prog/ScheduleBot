import asyncio
import logging

from aiogram import Dispatcher, Bot

from jsons.jsfiles import get_param
from handlers.data.writing import router_w
from handlers.data.redacting import router_out

logging.basicConfig(level=logging.INFO)
bot = Bot(token=get_param('Token'))
dp = Dispatcher()


async def main():
    dp.include_router(router_w)
    dp.include_router(router_out)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
