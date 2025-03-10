"""Server Telegram bot"""

import argparse
import os
import logging
from logging.handlers import RotatingFileHandler
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
import utils as ut

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LOG_MAX = 1  # Max size in MB of a log file
LOG_BCK_NUM = 2  # Max number of backup log files


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
    parser.add_argument("-l", "--log", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="",
                        help=("Enable and set the log level. Possible values are DEBUG, INFO, WARNING, ERROR, CRITICAL."
                              + " Default disabled."))
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
    logging.debug("Hello message sent")


if __name__ == '__main__':
    args = check_params()

    if args.log:
        file_path = os.path.dirname(os.path.abspath(__file__))

        logging.basicConfig(
            handlers=[RotatingFileHandler(
                f"{file_path}/bot.log",
                mode="a+",
                encoding="UTF-8",
                maxBytes=LOG_MAX * 1024 * 1024,
                backupCount=LOG_BCK_NUM),
                logging.StreamHandler()],
            level=getattr(logging, args.log),
            format="%(asctime)s:%(name)s:%(levelname)s: %(message)s"
        )

        # Disable the logs of other modules
        logging.getLogger("telegram").setLevel(logging.ERROR)
        logging.getLogger("apscheduler").setLevel(logging.ERROR)
        logging.getLogger("httpcore").setLevel(logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("asyncio").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)

    logging.info("Initializing bot...")
    logging.debug("Arguments: %s", args)
    logging.debug("Env var: BOT_TOKEN=%s",
                  TOKEN[:4] + '*' * (len(TOKEN) - 8) + TOKEN[-4:])
    logging.debug("Env var: CHAT_ID=%s", '*' *
                  (len(CHAT_ID) - 4) + CHAT_ID[-4:])
    logging.debug("Env var: STORAGE_PATHS=%s", os.getenv("STORAGE_PATHS"))
    logging.debug("Env var: NOTI_PATH=%s", os.getenv("NOTI_PATH"))

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('status', ut.status))
    application.add_handler(ut.reboot_handler)

    if args.hello:
        application.job_queue.run_once(send_startup_message, 0)

    if args.noti:
        logging.debug(
            "Notifications enabled. Checking every %s seconds.", args.time)

        if args.save_noti:
            logging.debug("Notifications will be stored after sending.")

        application.job_queue.run_repeating(
            ut.get_notifications, interval=args.time, data={"store": args.save_noti})

    logging.info("Bot started")
    application.run_polling()
