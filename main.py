"""Server Telegram bot"""

import argparse
import os
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
import utils as ut

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def check_params():
    """Check the input parameters.

    Returns:
        argparse.Namespace: Input parameters.
    """
    parser = argparse.ArgumentParser(
        description=(
            "It provides system information and incorporates a simple notification system from other scripts.")
    )
    parser.add_argument("--hello", action="store_true", default=False,
                        help="Send a message when the bot starts.")
    parser.add_argument("--noti", action="store_true", default=False,
                        help="Enable the notification check.")
    parser.add_argument("--save-noti", action="store_true", default=False,
                        help=("Notifications are not deleted after sending."
                              + " They are stored in a 'old' folder inside NOTI_PATH."))
    parser.add_argument("-t", "--time", type=int, default=10,
                        help="Time in seconds to check new notifications to be sent. Default 10.")

    return parser.parse_args()


async def send_startup_message(context: ContextTypes.DEFAULT_TYPE):
    """Say hello when the bot starts"""
    await context.bot.send_message(chat_id=CHAT_ID, text="👋 Hello! I'm up and running")


if __name__ == '__main__':
    args = check_params()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('status', ut.status))
    application.add_handler(ut.reboot_handler)

    if args.hello:
        application.job_queue.run_once(send_startup_message, 0)

    if args.noti:
        application.job_queue.run_repeating(
            ut.get_notifications, interval=args.time, data={"store": args.save_noti})

    application.run_polling()
