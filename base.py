import aiogram.fsm.state
from random import randint  # для случайного выбора
from data import *  # для хранения всякого
from aiogram import Bot, Dispatcher, Router, types, enums, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

r = Router()
types_for_comment = ['Фотография', 'Гифка', 'Текст']


def make_row_keyboard(items: list[str]) -> types.ReplyKeyboardMarkup:
    row = [types.KeyboardButton(text=item) for item in items]
    return types.ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class CommentSomething(StatesGroup):
    choosing_type_for_comment = State()
    commenting = State()


@r.message(CommentSomething.choosing_type_for_comment, F.text.in_(types_for_comment))
async def type_was_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() == 'фотография':
        picture_for_comment = types.FSInputFile(pictures[randint(1, 1)])
        await message.answer_photo(
            picture_for_comment,
            caption='Жду вашего комментария на следующую фотографию:',
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif message.text.lower() == 'гифка':
        gif_for_comment = types.FSInputFile(gifs[randint(1, 1)])
        await message.answer_video(
            gif_for_comment,
            caption='Жду вашего комментария на следующую гифку:',
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif message.text.lower() == 'текст':
        await message.answer(
            text='Ну тут типа текст какой-то, который нужно будет прокомментировать.',
            reply_markup=types.ReplyKeyboardRemove()
        )
    await state.set_state(CommentSomething.commenting)


@r.message(CommentSomething.choosing_type_for_comment)
async def type_chosen_incorrectly(message: types.Message):
    await message.answer(
        text="Написали же выбрать <b>тип контента</b>, просто <b>нажми на кнопку</b>!",
        reply_markup=make_row_keyboard(types_for_comment)
    )


@r.message(CommentSomething.commenting)
async def rate(message: types.Message, state: FSMContext):
    await message.answer(
        text='Ну тут типа будет оценка вашего комментария',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()


@r.message(CommandStart())
async def giving_a_choice(message: types.Message, state: FSMContext):
    await message.answer(
        text='И так, выберите контент, который хотите прокомментировать',
        reply_markup=make_row_keyboard(types_for_comment)
    )
    await state.set_state(CommentSomething.choosing_type_for_comment)


@r.message()
async def send_guide(message: types.Message):
    await message.answer(f'{message.from_user.first_name}, воспользуйтесь коммандой /start, пожалуйста.')
