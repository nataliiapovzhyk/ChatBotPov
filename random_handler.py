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


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Random handler is selected")
    prompt = load_prompt('random')
    chat_gpt.set_prompt(context, prompt)
    message = await send_text(update, context, "Зачекайте")
    response_text = await chat_gpt.send_message_list(context)
    #await send_text(update, context, response_text)
    await message.edit_text(response_text,reply_markup=get_random_keyboard())
    #update.message.reply_text(response_text, reply_markup=get_random_keyboard())