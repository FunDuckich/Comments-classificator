import sys
from config import API_TOKEN
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types, enums
from aiogram.filters import CommandStart

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Привет, {message.from_user.full_name}!")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Хорошая попытка, фрик")


async def main() -> None:
    bot = Bot(API_TOKEN, parse_mode=enums.ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())