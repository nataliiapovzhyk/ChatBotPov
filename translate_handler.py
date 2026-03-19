import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters

from gpt import chat_gpt
from keyboards import get_person_keyboard, get_end_keyboard, get_translate_keyboard
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, show_start_menu, BOT_COMMANDS)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

SELECT_LANG, TRANSLATE_TEXT = 1, 2

async def translate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Translate start is selected")
    prompt = load_prompt('translate')
    chat_gpt.set_prompt(context, prompt)

    text = load_message('translate')
    await send_image(update, context, 'translate')
    message = await send_text(update, context, text)
    await message.edit_text(text, reply_markup=get_translate_keyboard())
    return SELECT_LANG

    #message = await send_text(update, context, "Зачекайте")
    #response_text = await chat_gpt.send_message_list(context)
    #await send_text(update, context, response_text)
async def select_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Translate text is selected")
    query = update.callback_query
    await query.answer()
    language = query.data
    await chat_gpt.add_message(context, language)

    await query.message.reply_text("Введіть текст який треба перекласти")
    return TRANSLATE_TEXT

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_to_translate = update.message.text
    response = await chat_gpt.add_message(context, text_to_translate)
    await send_text(update, context, response)
    return ConversationHandler.END

translate_handler = ConversationHandler(

    entry_points=[
        CommandHandler("translate", translate_start)
    ],

    states={
        SELECT_LANG: [
            CallbackQueryHandler(select_lang, pattern="^translate_")
        ],
        TRANSLATE_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text),
            CallbackQueryHandler(translate_text, pattern="^end_translate")
        ]
    },

    fallbacks=[]
)