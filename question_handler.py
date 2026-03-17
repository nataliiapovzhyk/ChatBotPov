import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters

from gpt import  chat_gpt
from keyboards import get_random_keyboard
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ASK_GPT = 1
async def gpt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("GPT Question is selected")
    text = load_message('gpt')
    await send_image(update, context, 'gpt')
    logger.info("Waiting question typing")
    await update.message.reply_text(text)
    return ASK_GPT

async def gpt_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Asking user question")
    user_text = update.message.text
    message = await update.message.reply_text("Думаю...")
    prompt = load_prompt('gpt')
    response_text = await chat_gpt.send_question(context,prompt,user_text)

    await message.edit_text(response_text)

    return ConversationHandler.END

gpt_handler = ConversationHandler(

    entry_points=[
        CommandHandler("gpt", gpt_start)
    ],

    states={
        ASK_GPT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_question)
        ]
    },

    fallbacks=[]
)
