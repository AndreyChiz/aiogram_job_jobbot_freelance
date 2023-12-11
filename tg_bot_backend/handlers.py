from aiogram import Bot
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from tg_bot_backend.keyboards import control_panel
from tg_bot_backend.lexicon import lexicon_ru_txt

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_handler(message: Message):
    '''
    Обработчик команды /start. Предоставляет пользователю клавиатуру control_panel
    '''
    await message.answer(f'Приветствую {hbold(message.from_user.first_name)}!\n{lexicon_ru_txt["greeteng"]}',
                         reply_markup=control_panel)
    # print(*message, sep='\n')


@router.message(Command('settings'))
async def show_control_panel(message: Message):
    """
    Отображает основную клавиатуру control_panel при отправке /settings или нажати на кнопку в меню команд
    """
    await message.answer('Настройки: ', reply_markup=control_panel)  # TODO: поместить в lexicon


class Autor(StatesGroup):
    """
    Состояние отправки сообщения разработчику
    """
    autor_message = State()


@router.message(Command('hello'))
async def show_control_panel(message: Message, state: FSMContext):
    """
    Обработка команды /hello
    - переключает в состояние ввода сообщения разработчику
    - выводит приглашение ввести сообщение разработчику
    """
    await state.set_state(Autor.autor_message)
    await message.answer('Сообщение разработчику')  # TODO: поместить в lexicon


@router.message(Autor.autor_message)
async def get_keywords(message: Message, bot: Bot, state: FSMContext):
    """
    Принимает сообщение от пользователя и отправляет разработчику
    """
    data = await state.update_data(
        autor_message=f'Сообщение от: {message.from_user.username}, id: {message.from_user.id}\n{message.text} ')
    await bot.send_message(1814523536, data['autor_message'])
    print(data)
    await state.clear()


class KeyWords(StatesGroup):
    """
    Состояние ввода ключевых слов
    """
    keywords = State()

#
# @router.callback_query()
# async def callback_query_handler(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
#     """
#     Обработчки нажатий кнопок control_panel
#     """
#     if callback_query.data == 'enter_keywords':
#         await state.set_state(KeyWords.keywords)
#         await bot.send_message(callback_query.from_user.id, "Введите ключевые слова:")  # TODO: поместить в lexicon
#
#     elif callback_query.data == 'start_notyfy':
#         await db_write_is_notified(callback_query.from_user.id, 1, )
#         await bot.send_message(callback_query.from_user.id,
#                                "Отправка  уведомлений активирована")  # TODO: поместить в lexicon
#
#     elif callback_query.data == 'stop_notyfy':
#         await db_write_is_notified(callback_query.from_user.id, 0)
#         await bot.send_message(callback_query.from_user.id,
#                                "Отправка уведомлений приостановлена")  # TODO: поместить в lexicon
#
#
# @router.message(KeyWords.keywords)
# async def get_keywords(message: Message, state: FSMContext):
#     """
#     Принимает от пользователя ключевые слова и пишет их в базу данных
#     """
#     data = await state.update_data(keywords=message.text)
#     await db_write_key_words(user_id=message.from_user.id, keywords=data['keywords'])
#     await message.answer(f'Ключевые слова | {" | ".join(data["keywords"].split(","))} | успешно добавлены',
#                          reply_markup=control_panel)  # TODO: поместить в lexicon
#     await state.clear()
