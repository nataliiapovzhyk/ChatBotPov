import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters

from gpt import chat_gpt
from keyboards import get_person_keyboard, get_end_keyboard, get_translate_keyboard, get_translate_change_keyboard, \
    get_words_keyboard
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, show_start_menu, BOT_COMMANDS)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

SELECT_MODE, LEARN_MODE, TEST_MODE, STATS_MODE = 1, 2, 3, 4

async def words_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Words start is selected")
    prompt = load_prompt('words')
    chat_gpt.set_prompt(context, prompt)

    text = load_message('words')
    await send_image(update, context, 'words')
    message = await send_text(update, context, text)
    await message.edit_text(text, reply_markup=get_words_keyboard())
    return SELECT_MODE

async def words_learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END

words_handler = ConversationHandler(

    entry_points=[
        CommandHandler("words", words_start)
    ],

    states={
        SELECT_MODE: [
            CallbackQueryHandler(words_learn, pattern="^words_.*")
        ],
        LEARN_MODE: [

        ]
    },

    fallbacks=[]
)