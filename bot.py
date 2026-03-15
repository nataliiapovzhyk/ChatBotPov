import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler

from gpt import ChatGptService
from keyboards import get_random_keyboard
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt)
from credentials import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start menu is selected")
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓'
        # Додати команду в меню можна так:
        # 'command': 'button text'


    })
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Randomw is selected")
    prompt = load_prompt('random')
    chat_gpt.set_prompt(prompt)
    message = await send_text(update, context, "Зачекайте")
    response_text = chat_gpt.send_message_list()
    #await send_text(update, context, response_text)
    await message.edit_text(response_text,reply_markup=get_random_keyboard())
    #update.message.reply_text(response_text, reply_markup=get_random_keyboard())


chat_gpt = ChatGptService(config.ChatGPT_TOKEN)
app = ApplicationBuilder().token(config.BOT_TOKEN).build()

# Зареєструвати обробник команди можна так:
# app.add_handler(CommandHandler('command', handler_func))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))

app.add_handler(CallbackQueryHandler(random, pattern="random"))
app.add_handler(CallbackQueryHandler(start, pattern="start"))



# Зареєструвати обробник колбеку можна так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
#app.add_handler(CallbackQueryHandler(default_callback_handler))

logger.info("bot started")
app.run_polling()
