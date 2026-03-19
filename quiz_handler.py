import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, \
    MessageHandler, filters, CallbackContext

from gpt import  chat_gpt
from keyboards import get_random_keyboard, get_quiz_topic_keyboard, get_quiz_play_keyboard
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, show_start_menu)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

SELECT_TOPIC, ANSWER_QUIZ = 1, 2

def get_results(context: ContextTypes.DEFAULT_TYPE):
    if "quiz_results" not in context.user_data:
        context.user_data["quiz_results"] = {
            "total" : 0,
           "correct_total": 0
           }
    return context.user_data["quiz_results"]

async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Quiz menu is selected")
    get_results(context)
    context.user_data["quiz_results"] = {
        "total": 0,
        "correct_total": 0
    }



    await send_image(update, context, 'quiz')
    logger.info(f"Chat ID: {update.effective_chat.id}: QUIZ _ Waiting topic selection")
    prompt = load_prompt('quiz')
    chat_gpt.set_prompt(context, prompt)

    text = load_message('quiz')
    await update.message.reply_text(text, reply_markup=get_quiz_topic_keyboard())
    return SELECT_TOPIC

async def quiz_change_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Quiz change topic is ongoing ")
    text = load_message('quiz')

    message = await send_text(update, context, "Думаю...")
    await message.edit_text(text, reply_markup=get_quiz_topic_keyboard())

    return SELECT_TOPIC

async def quiz_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Quiz play is ongoing ")
    query = update.callback_query
    await query.answer()

    context.user_data["quiz_results"]["total"] += 1

    question = await chat_gpt.add_message(context, query.data)

    await query.message.reply_text(question, reply_markup=get_quiz_play_keyboard())

    return ANSWER_QUIZ

async def quiz_check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Quiz check answer is ongoing ")
    user_answer = update.message.text
    gpt_evaluation = await chat_gpt.add_message(context, user_answer)

    if "Правильно" in gpt_evaluation:
        context.user_data["quiz_results"]["correct_total"] += 1

    message = await send_text(update, context, "Перевіряю...")
    await message.edit_text(gpt_evaluation, reply_markup=get_quiz_play_keyboard())

    return ANSWER_QUIZ

async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Chat ID: {update.effective_chat.id}: Quiz end selected")
    total = context.user_data["quiz_results"]["total"]
    correct = context.user_data["quiz_results"]["correct_total"]
    await send_text(update, context, f"Всього зіграно питань: {total}. З них вірно: {correct}. Результат: {correct / total}")

    await show_start_menu(update, context)
    return ConversationHandler.END

quiz_handler = ConversationHandler(

    entry_points=[
        CommandHandler("quiz", quiz_start)
    ],

    states={
        SELECT_TOPIC: [
            CallbackQueryHandler(quiz_play, pattern="^quiz_")
        ],
        ANSWER_QUIZ: [
            CallbackQueryHandler(quiz_play, pattern="^quiz_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_check_answer),
            CallbackQueryHandler(quiz_change_topic, pattern="^topic_quiz"),
            CallbackQueryHandler(end_quiz, pattern="^end_quiz")

        ]
    },

    fallbacks=[]
)
