from random import randint
from data import *
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import utils


max_comment_len = 12
vector_size = 300


r = Router()
types_for_comment = ['Фотографию', 'Гифку', 'Текст']


def make_row_keyboard(items: list[str]) -> types.ReplyKeyboardMarkup:
    row = [types.KeyboardButton(text=item) for item in items]
    return types.ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class CommentSomething(StatesGroup):
    choosing_type_for_comment = State()
    commenting = State()


@r.message(CommentSomething.choosing_type_for_comment, F.text.in_(types_for_comment))
async def type_was_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() == 'фотографию':
        picture_for_comment = types.FSInputFile(pictures[randint(1, max(pictures.keys()))])
        await message.answer_photo(
            photo=picture_for_comment,
            caption='Жду вашего комментария на следующую фотографию:',
            reply_markup=types.ReplyKeyboardRemove()  # удаляем кнопки, иначе так и будут висеть
        )
    elif message.text.lower() == 'гифку':
        await message.answer_animation(  # отправляем гифку
            animation=gifs[randint(1, max(gifs.keys()))],
            caption='Жду вашего комментария на следующую гифку:',
            reply_markup=types.ReplyKeyboardRemove()  # удаляем кнопки, иначе так и будут висеть
        )
    elif message.text.lower() == 'текст':
        await message.answer(
            text=f'Жду вашего комментария на следующий текст: \n\n{quotes[randint(1, max(quotes.keys()))]}',
            reply_markup=types.ReplyKeyboardRemove()  # удаляем кнопки, иначе так и будут висеть
        )
    await state.set_state(CommentSomething.commenting)


@r.message(CommentSomething.choosing_type_for_comment)
async def type_chosen_incorrectly(message: types.Message):
    await message.answer(
        text="Написали же выбрать <b>тип контента</b>, просто <b>нажми на кнопку</b>!",
        reply_to_message_id=message.message_id,
        reply_markup=make_row_keyboard(types_for_comment)
    )


@r.message(CommentSomething.commenting)
async def rate(message: types.Message, state: FSMContext):
    result = utils.get_result(message.text) * 100
    if result < 50:
        await message.answer(
            text=f'Я на {int(abs(100 - result))}% уверен, что это негативный комментарий!',
            reply_to_message_id=message.message_id,
            reply_markup=types.ReplyKeyboardRemove()  # удаляем кнопки, иначе так и будут висеть
        )
    else:
        await message.answer(
            text=f'Я на {int(result)}% уверен, что это положительный комментарий!',
            reply_to_message_id=message.message_id,
            reply_markup=types.ReplyKeyboardRemove()  # удаляем кнопки, иначе так и будут висеть
        )
    await state.clear()


@r.message(CommandStart())
async def giving_a_choice(message: types.Message, state: FSMContext):
    await message.answer(
        text='И так, выберите контент, который хотите прокомментировать.',
        reply_to_message_id=message.message_id,
        reply_markup=make_row_keyboard(types_for_comment)
    )
    await state.set_state(CommentSomething.choosing_type_for_comment)


@r.message()
async def send_guide(message: types.Message):
    await message.answer(f'{message.from_user.first_name}, воспользуйтесь коммандой /start, пожалуйста.',
                         reply_to_message_id=message.message_id)
