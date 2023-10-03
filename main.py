import sys
from config import API_TOKEN
from base import r
import asyncio
import logging
from aiogram import Bot, Dispatcher, enums


async def main() -> None:
    bot = Bot(API_TOKEN, parse_mode=enums.ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router=r)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    asyncio.run(main())
