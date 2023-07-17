from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_kb() ->ReplyKeyboardMarkup:
    """создание клавиатуры для пользователя 

    Returns:
        ReplyKeyboardMarkup: клавиатура для пользователя
    """
    
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    
    b1 = KeyboardButton("✏️ Запланировать задачу")
    b2 = KeyboardButton("📄 Показать список задач")
    kb.add(b1, b2)
    
    return kb 


def get_cancel_kb() -> ReplyKeyboardMarkup:
    """создание клавиатуры для отмены действия пользователя

    Returns:
        ReplyKeyboardMarkup: клавиатура для пользователя
    """
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("❌ Отмена"))

