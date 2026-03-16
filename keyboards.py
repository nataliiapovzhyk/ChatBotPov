from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Update

REPLY_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Кнопка 1"), KeyboardButton("Кнопка 2")],
        [KeyboardButton("Прибрати клавіатуру")]
    ],
    resize_keyboard=True
)

def get_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("OK", callback_data="like"),
            InlineKeyboardButton("notOK", callback_data="dislike")
        ],
        [InlineKeyboardButton("Details -> ", url = "https://google.com" )]
    ])

def get_random_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Хочу ще факт", callback_data="random"),
            InlineKeyboardButton("Закінчити", callback_data="start")
        ]
    ])

def get_person_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1", callback_data="talk_cobain"),
            InlineKeyboardButton("2", callback_data="talk_queen"),
            InlineKeyboardButton("3", callback_data="talk_tolkien"),
            InlineKeyboardButton("4", callback_data="talk_nietzsche"),
            InlineKeyboardButton("5", callback_data="talk_hawking")
        ]
    ])

def get_end_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Закінчити", callback_data="end_talk")
        ]
    ])