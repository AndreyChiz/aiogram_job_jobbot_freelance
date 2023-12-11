from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tg_bot_backend.lexicon import lexicon_ru_buttons

btn_start_notify = InlineKeyboardButton(text=lexicon_ru_buttons['btn_start_notify'], callback_data='start_notyfy')
btn_create_key_words_list = InlineKeyboardButton(text='Ввести ключевые слова', callback_data='enter_keywords')
btn_stop_notify = InlineKeyboardButton(text='Прекратить уведомления', callback_data='stop_notyfy')


'''
control_panel - основная клавиатура при помощи которой присходит всё взаимодействие с ботом
'''
control_panel_buttons = [[btn_start_notify],
                         [btn_create_key_words_list],
                         [btn_stop_notify]
                         ]


control_panel = InlineKeyboardMarkup(inline_keyboard=control_panel_buttons)

