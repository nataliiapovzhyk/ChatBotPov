import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters


from question_handler import  gpt_handler
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



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start menu is selected")
    await show_start_menu(update, context)


app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_error_handler(error_handler)
# Зареєструвати обробник команди можна так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))


app.add_handler(CallbackQueryHandler(random, pattern="random"))
app.add_handler(CallbackQueryHandler(start, pattern="start"))


app.add_handler(gpt_handler)
app.add_handler(talk_handler)
# Зареєструвати обробник колбеку можна так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
#app.add_handler(CallbackQueryHandler(default_callback_handler))

logger.info("bot started")
app.run_polling()
