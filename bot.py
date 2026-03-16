import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters

from gpt import ChatGptService, chat_gpt
from keyboards import get_random_keyboard
from random_handler import random
from talk_handler import talk_handler
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, show_start_menu)
from credentials import config

from error_handler import error_handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ASK_GPT = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start menu is selected")
    await show_start_menu(update, context)



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
    response_text = await chat_gpt.send_question(prompt,user_text)

    await message.edit_text(response_text)

    return ConversationHandler.END



app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_error_handler(error_handler)
# Зареєструвати обробник команди можна так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))


app.add_handler(CallbackQueryHandler(random, pattern="random"))
app.add_handler(CallbackQueryHandler(start, pattern="start"))


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

app.add_handler(gpt_handler)
app.add_handler(talk_handler)
# Зареєструвати обробник колбеку можна так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
#app.add_handler(CallbackQueryHandler(default_callback_handler))

logger.info("bot started")
app.run_polling()
