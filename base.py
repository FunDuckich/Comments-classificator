from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


r = Router()  # хуйня, вам это не важно
types_for_comment = ['Фотографию', 'Гифку', 'Текст']  # типы контента, которые пользователи выбирают


def make_row_keyboard(items: list[str]) -> types.ReplyKeyboardMarkup:  # хуйнюшка генерирует кнопки на клаве
    row = [types.KeyboardButton(text=item) for item in items]
    return types.ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


class CommentSomething(StatesGroup):  # Класс машины состояний, в котором есть два состояния
    choosing_type_for_comment = State()
    commenting = State()


@r.message(CommentSomething.choosing_type_for_comment, F.text.in_(types_for_comment))  # ловит сообщения первого состояния
async def type_was_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() == 'фотографию':  # если выбрали фотографию
        picture_for_comment = types.FSInputFile("picture.jpeg")  #здесь вот выбирается фотография
        await message.answer_photo(  #здесь фотка отправляется
            picture_for_comment,
            caption='Жду вашего комментария на следующую фотографию:',
            reply_markup=types.ReplyKeyboardRemove()  # убираем наши кнопки
        )
    elif message.text.lower() == 'гифку':  # если выбрали гифку
        gif_for_comment = types.FSInputFile("roach-dancing.mp4")  # здесь выбирается файл
        await message.answer_video(  # отправляется гифка в формате видео (по-другому никак)
            gif_for_comment,
            caption='Жду вашего комментария на следующую гифку:',
            reply_markup=types.ReplyKeyboardRemove()  # убираем наши кнопки
        )
    else:  # если выбрали текст
        # здесь нужно реализовать выбор текста из файла
        await message.answer(  #отправляется текст
            text='Ну тут типа текст какой-то, который нужно будет прокомментировать.',
            reply_markup=types.ReplyKeyboardRemove()  # убираем наши кнопки
        )
    await state.set_state(CommentSomething.commenting)


@r.message(CommentSomething.choosing_type_for_comment)  # если предыдущий декоратор не поймал сообщение,
async def type_chosen_incorrectly(message: types.Message):  # то мы обрабатываем его как ошибку
    await message.answer(
        text="Написали же выбрать <b>тип контента</b>, просто <b>нажми на кнопку</b>!",
        reply_markup=make_row_keyboard(types_for_comment)  # нашей функцией генерируем те самые кнопки
    )


@r.message(CommentSomething.commenting)  # ловим второе состояние (когда пользователем комментируется что-то)
async def rate(message: types.Message, state: FSMContext):
    # здесь я оценю комментарий нейросеткой и нужно будет в зависимости от того, положительный он или отрицателный, из
    # разных файлов выбрать рандомное сообщение пользователю
    await message.answer(
        text='Ну тут типа будет оценка вашего комментария',
        reply_markup=types.ReplyKeyboardRemove()  # убираем наши кнопки
    )
    await state.clear()  # прерываем нашу цепочку состояний


@r.message(CommandStart())  # здесь обработка команды '/start'
async def giving_a_choice(message: types.Message, state: FSMContext):
    await message.answer(
        text='И так, выберите контент, который хотите прокомментировать',
        reply_markup=make_row_keyboard(types_for_comment)  # нашей функцией генерируем те самые кнопки
    )
    await state.set_state(CommentSomething.choosing_type_for_comment)  # начинаем цепочку состояний


@r.message()  # обрабатываем все обычные сообщения
async def send_guide(message: types.Message):
    await message.answer(f'{message.from_user.first_name}, воспользуйтесь коммандой /start, пожалуйста.')
