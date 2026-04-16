import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters

from gpt import chat_gpt
from keyboards import get_person_keyboard, get_end_keyboard, get_translate_keyboard, get_translate_change_keyboard, \
    get_words_keyboard, get_words_learn_keyboard, get_words_test_keyboard
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, show_start_menu, BOT_COMMANDS)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


words_list_full = None
with open("resources/prompts/words_list.txt", "r", encoding="utf8") as file:
    words_list_full = [line.strip() for line in file]



def get_watched_list(context: ContextTypes.DEFAULT_TYPE) -> list:
    if "watched_list" not in context.user_data:
        context.user_data["watched_list"] = []
    return context.user_data["watched_list"]

def get_learned_list(context: ContextTypes.DEFAULT_TYPE) -> list:
    if "learned_list" not in context.user_data:
        context.user_data["learned_list"] = []
    return context.user_data["learned_list"]

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
    logger.info(f"Chat ID: {update.effective_chat.id}: Words learn is selected ")
    query = update.callback_query
    await query.answer()

    await chat_gpt.add_message(context, query.data)
    message = await send_text(update, context, "Підбираю цікаве слово для вивчення...")

    words_list = None
    if query.data == "words_learn":
        words_list  = list(set(words_list_full) - set(get_watched_list(context)) - set(get_learned_list(context)))
    elif query.data == "words_repeat":
        words_list = get_watched_list(context) + get_learned_list(context)

    item = random.choice(words_list).strip()
    response = await chat_gpt.add_message(context, item)

    await message.edit_text(response, reply_markup=get_words_learn_keyboard(), parse_mode="html")

    if item not in get_watched_list(context):
        get_watched_list(context).append(item)

    return LEARN_MODE

async def words_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Words test is selected ")

    query = update.callback_query
    await query.answer()
    logger.info(query.data)

    list_to_test = get_watched_list(context)

    item = random.choice(list_to_test).strip()
    context.user_data["item_tested"] = item

    logger.info(item)

    await chat_gpt.add_message(context, f"{query.data}-{item}")

    await query.message.reply_text(f"Який переклад для фрази {item}")


    return TEST_MODE

async def words_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Check test is selected ")
    translation_to_verify = update.message.text
    logger.info(translation_to_verify)
    message = await send_text(update, context, "Перевіряю")
    response = await chat_gpt.add_message(context, translation_to_verify)
    if response.find("Невірно") == -1:
        get_learned_list(context).append(context.user_data["item_tested"])
        get_watched_list(context).remove(context.user_data["item_tested"])

    logger.info(get_watched_list(context))
    logger.info(get_learned_list(context))

    await message.edit_text(response, reply_markup=get_words_test_keyboard(), parse_mode="html")
    return SELECT_MODE

async def words_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Words stat is selected ")

    query = update.callback_query
    await query.answer()

    await query.message.reply_text(f"Всього вивчено слів: {len(get_learned_list(context))}")
    await query.message.reply_text(f"Переглянуто: {len(get_watched_list(context))}")
    await query.message.reply_text(f"Всього залишилось: {len(set(words_list_full)-set(get_learned_list(context))-set(get_watched_list(context)))}")
    await show_start_menu(update, context)

    return ConversationHandler.END

words_handler = ConversationHandler(

    entry_points=[
        CommandHandler("words", words_start)
    ],

    states={
        SELECT_MODE: [
            CallbackQueryHandler(words_learn, pattern="^words_learn"),
            CallbackQueryHandler(words_test, pattern="^words_test"),
            CallbackQueryHandler(words_stat, pattern="^words_stat")
        ],
        LEARN_MODE: [
            CallbackQueryHandler(words_learn, pattern="^words_learn"),
            CallbackQueryHandler(words_learn, pattern="^words_repeat"),
            CallbackQueryHandler(words_test, pattern="^words_test")
        ],
        TEST_MODE: [
            CallbackQueryHandler(words_test, pattern="^words_test"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, words_check)
        ]
    },

    fallbacks=[]
)