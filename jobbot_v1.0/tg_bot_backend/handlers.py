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

from database import Database
from logger import logger

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_handler(message: Message):
    '''
    Start command handler. Provides the user with a keyboard control_panel
    '''
    await message.answer(f'Приветствую {hbold(message.from_user.first_name)}!\n{lexicon_ru_txt["greeteng"]}',
                         reply_markup=control_panel)
    # print(*message, sep='\n')


@router.message(Command('settings'))
async def show_control_panel(message: Message):
    """
    Displays the main keyboard control_panel when submitting settings or clicking a button in the command menu
    """
    await message.answer('Настройки: ', reply_markup=control_panel)  # TODO: поместить в lexicon


class Autor(StatesGroup):
    """
    Status of message sent to developer
    """
    autor_message = State()


@router.message(Command('hello'))
async def show_control_panel(message: Message, state: FSMContext):
    """
    - switches to the state of entering a message to the developer
    - displays a prompt to enter a message to the developer
    """
    await state.set_state(Autor.autor_message)
    await message.answer('Сообщение разработчику')  # TODO: поместить в lexicon


@router.message(Autor.autor_message)
async def get_keywords(message: Message, bot: Bot, state: FSMContext):
    """
    Receives a message from the user and sends it to the developer
    """
    data = await state.update_data(
        autor_message=f'Сообщение от: {message.from_user.username}, id: {message.from_user.id}\n{message.text} ')
    await bot.send_message(1814523536, data['autor_message'])
    logger.debug(data)
    await state.clear()


class KeyWords(StatesGroup):
    """
    Keyword input status
    """
    keywords = State()


@router.callback_query()
async def callback_query_handler(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Handling button clicks control_panel
    """
    if callback_query.data == 'enter_keywords':
        await state.set_state(KeyWords.keywords)
        await bot.send_message(callback_query.from_user.id, "Введите ключевые слова:")  # TODO: поместить в lexicon

    elif callback_query.data == 'start_notyfy':
        await Database().insert_user_data(user_id=callback_query.from_user.id,
                                            user_notify=True)
        await bot.send_message(callback_query.from_user.id,
                               "Отправка  уведомлений активирована")  # TODO: поместить в lexicon

    elif callback_query.data == 'stop_notyfy':
        await Database().insert_user_data(user_id=callback_query.from_user.id,
                                          user_notify=False)
        await bot.send_message(callback_query.from_user.id,
                               "Отправка уведомлений приостановлена")  # TODO: поместить в lexicon


@router.message(KeyWords.keywords)
async def get_keywords(message: Message, state: FSMContext):
    """
    Receives keywords from the user and writes them to the database
    """
    data = await state.update_data(keywords=message.text)
    await Database().insert_user_data(user_id=message.from_user.id,
                                      user_name=message.from_user.username,
                                      user_keywords=data['keywords'],
                                      user_notify=True)
    await message.answer(f'Ключевые слова | {" | ".join(list(set(data["keywords"].split(","))))} | успешно добавлены',
                         reply_markup=control_panel)  # TODO: поместить в lexicon
    await state.clear()
