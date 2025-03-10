"""Commands"""

import os
import logging
from telegram import Update
import telegram
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

CHOOSING = range(1)


async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reboot the system"""

    logging.debug("Reboot command received")

    reply_markup = telegram.ReplyKeyboardMarkup(
        [["Yes", "No"]], one_time_keyboard=True)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Are you sure to reboot the system?",
                                   reply_markup=reply_markup)

    return CHOOSING


async def check_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the user response"""
    response = update.message.text.lower()

    logging.debug("User response: %s", response)

    if response == "yes":
        await context.bot.send_message(chat_id=os.getenv("CHAT_ID"),
                                       text="Rebooting the system... 🔄",
                                       parse_mode="HTML",
                                       reply_markup=telegram.ReplyKeyboardRemove())
        os.system("sudo reboot")
        logging.debug("Rebooting the system...")

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Reboot cancelled",
                                       reply_markup=telegram.ReplyKeyboardRemove())
        logging.debug("Reboot cancelled")

    return ConversationHandler.END

reboot_handler = ConversationHandler(
    entry_points=[CommandHandler('reboot', reboot)],
    states={
        CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_response)],
    },
    fallbacks=[],
)
