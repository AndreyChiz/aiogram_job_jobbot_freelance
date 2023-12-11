from aiogram.utils.markdown import hbold, hcode, hitalic

lexicon_ru_buttons = {
    "btn_start_notify": "Активировать уведомления",
    "btn_create_key_words_list": "Ввести ключевые слова",
    "btn_stop_notify": "Прекратить уведомления"
}

lexicon_ru_txt = {"greeteng": f'''
Всё просто как раз, два, три!
1. Нажми {hbold(f'"{lexicon_ru_buttons["btn_create_key_words_list"]}"')}
2. Отправь в сообщении ключевые слова для подбора заказов.
{hitalic('пример: python, бот, aiogram, flask')}
3. Нажми {hbold(f'"{lexicon_ru_buttons["btn_start_notify"]}"')}
'''
}
