import logging
import traceback

from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update")
    logger.error("Update: %s", update)
    logger.error("Error: %s", context.error)
    traceback_str = "".join(traceback.format_exception(None, context.error, context.error.__traceback__))

    logger.error("Traceback:\n%s", traceback_str)