from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext, MessageHandler, filters, \
    CallbackQueryHandler
from config import Config, config
from keyboards import REPLY_KEYBOARD, get_keyboard


async def start_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт друже!", reply_markup=get_keyboard())

async def answer(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

async def answer_button(update: Update, context: CallbackContext):
    if update.message.text == "Кнопка 1":
        await update.message.reply_text("кнопка 1")
    elif update.message.text == "Кнопка 2":
        await update.message.reply_text("кнопка 2")

async def remove_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Клавіатуру очищено!", reply_markup=ReplyKeyboardRemove())


async def login(update: Update, context: CallbackContext):

    password = context.args[0] if context.args else None

    if not password:
        await update.message.reply_text("Введіть пароль")
        return
    if password == config.admin_password:
        await update.message.reply_text("Доступ надано")
        context.user_data['is_admin'] = True
    else:
        await update.message.reply_text("Неправильний пароль")

async def get_data(update: Update, context: CallbackContext):
    if context.user_data.get("is_admin", False):
        await update.message.reply_text("Ось дані")
        await answer_chat_info(update, context, ">>>>")
    else:
        await update.message.reply_text("Потрібен доступ")

async def answer_chat_info(update: Update, context: CallbackContext, prefix = ""):
    chat = update.effective_chat
    info = f"{prefix}Chat ID: {chat.id}, Type: {chat.type}"
    await context.bot.send_message(chat_id=chat.id, text=info)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query



    if query.data == "like":
        await update.effective_chat.send_message("Дякую за Ок")
    elif query.data == "dislike":
        await update.effective_chat.send_message("Отримали не Ок")

    await query.answer()


if __name__ == '__main__':
    application = ApplicationBuilder().token(Config.token).build()

    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    application.add_handler(CommandHandler('start', start_func))
    application.add_handler(CommandHandler('login', login))
    application.add_handler(CommandHandler('get_data', get_data))

    application.add_handler(MessageHandler(filters.Text(("Кнопка 1", "Кнопка 2")), answer_button))
    application.add_handler(MessageHandler(filters.Text(("Прибрати клавіатуру",)), remove_keyboard))

    application.add_handler(CallbackQueryHandler(callback_handler))
    print("бота запущено")
    application.run_polling()