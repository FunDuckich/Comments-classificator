from random import randint  # для случайного выбора


from data import *
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import pickle
from nltk.corpus import stopwords
import pymystem3
from navec import Navec
import re
import numpy as np


max_comment_len = 10
vector_size = 300


def clear_text(text: str) -> str:
    cleared_text = re.sub(r'[^А-яЁё]+', ' ', text).lower()
    return ' '.join(cleared_text.split())


def tokenize(text: str) -> list:
    result = []
    k = m.lemmatize(text)
    for word in k:
        if word != ' ' and word != '\n' and not(word in russian_stopwords):
            result.append(word)
    return result


def vectorize_tokens(tokens: list, nvc, max_len: int) -> list:
    unk = nvc['<unk>']
    text_embeddings = []
    for tocken in tokens:
        embedding = nvc.get(tocken, unk)
        text_embeddings.append(embedding)

    ln = len(text_embeddings)

    if ln > max_len:
        text_embeddings = text_embeddings[:max_len]
    else:
        text_embeddings = [nvc['<pad>']] * (max_len - ln) + text_embeddings

    return text_embeddings


def get_result(sentence: str) -> list:
    tokens = tokenize(clear_text(sentence))

    vectors = vectorize_tokens(tokens, navec, max_comment_len)
    vectors = np.array([vectors]).reshape(1, 3000)

    prediction = model.predict_proba(vectors)[0]
    negative_confidence = prediction[0]
    positive_confidence = prediction[1]

    if negative_confidence > positive_confidence:
        return [negative_confidence, 0, tokens]
    elif negative_confidence < positive_confidence:
        return [positive_confidence, 1, tokens]
    else:
        return [positive_confidence, 2, tokens]


m = pymystem3.Mystem()
filename = 'navec_Sklearn_MLPClassifier.sav'
russian_stopwords = stopwords.words("russian")
navec = Navec.load('navec_hudlit_v1_12B_500K_300d_100q.tar')
model = pickle.load(open(filename, 'rb'))


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
            text=f'Жду вашего комментария на следующий текст: \n\n{texts[randint(1, max(texts.keys()))]}',
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
    result = get_result(message.text)
    if result[1] == 0:
        await message.answer(
            text=f'Я на {result[0]:.0%} уверен, что это негативный комментарий!',
            reply_to_message_id=message.message_id,
            reply_markup=types.ReplyKeyboardRemove()  # удаляем кнопки, иначе так и будут висеть
        )
    elif result[1] == 1:
        await message.answer(
            text=f'Я на {result[0]:.0%} уверен, что это положительный комментарий!',
            reply_to_message_id=message.message_id,
            reply_markup=types.ReplyKeyboardRemove()  # удаляем кнопки, иначе так и будут висеть
        )
    else:
        await message.answer(
            text=f'Честно..? Я не знаю, как оценить твой комментарий.\n'
                 f'А вот слова, которые я в нём обнаружил: {result[2]}',
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
