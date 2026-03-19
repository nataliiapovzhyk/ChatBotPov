import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters

from gpt import chat_gpt
from keyboards import get_person_keyboard, get_end_keyboard
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, show_start_menu, BOT_COMMANDS)
from credentials import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


SELECT_PERSON, TALK_TO_PERSON = 1, 2

async def talk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Talk menu is selected")

    await send_image(update, context, 'talk')
    logger.info(f"Chat ID: {update.effective_chat.id}: Waiting selection")
    text = load_message('talk')
    await update.message.reply_text(text, reply_markup=get_person_keyboard())
    return SELECT_PERSON

async def connect_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}:Hero menu is selected")
    query = update.callback_query
    await query.answer()

    person = query.data.replace("talk_", "")
    context.user_data["person"] = person
    prompt = load_prompt(query.data)
    chat_gpt.set_prompt(context,prompt)

    await send_image(update, context, query.data)

    message = await send_text(update, context,"Твій співбесідник під'єднується, зачекай...")


    response_text = await chat_gpt.send_message_list(context)

    await message.edit_text(response_text)

    return TALK_TO_PERSON


async def talk_to_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Запитання отримали")
    question = update.message.text

    message = await send_text(update, context, "Думаю...")

    logger.info(f"Chat ID: {update.effective_chat.id}: Надсилаємо запит до GPT")
    response_text = await chat_gpt.add_message(context, question)

    await message.edit_text(response_text, reply_markup=get_end_keyboard())

    return TALK_TO_PERSON

async def end_talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: end talk selected")
    await send_text(update, context, "Розмову завершено.")
    await show_start_menu(update, context)
    return ConversationHandler.END

talk_handler = ConversationHandler(

    entry_points=[
        CommandHandler("talk", talk_start)
    ],

    states={
        SELECT_PERSON: [
            CallbackQueryHandler(connect_person, pattern="^talk_")
        ],
        TALK_TO_PERSON: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, talk_to_person),
            CallbackQueryHandler(end_talk, pattern="^end_talk")
        ]
    },

    fallbacks=[]
)

