# pylint: disable=broad-except
"""Notifications"""

import os
import logging
import time
from datetime import datetime
from telegram.ext import ContextTypes


async def get_notifications(context: ContextTypes.DEFAULT_TYPE):
    """Check the notifications and send them to the chat"""

    store = context.job.data.get("store", True)

    noti_path = os.getenv("NOTI_PATH")

    if noti_path:
        try:
            files = [f for f in os.listdir(
                noti_path) if os.path.isfile(os.path.join(noti_path, f))]
            files_with_dates = [(file, os.path.getctime(
                os.path.join(noti_path, file))) for file in files]

            files_with_dates.sort(key=lambda x: x[1])

            if len(files_with_dates) != 0:
                logging.debug("New files detected: %s", len(files_with_dates))

            for file, ctime in files_with_dates:
                logging.debug("[%s] Posix_time=%s", file, int(ctime))
                time_str = datetime.fromtimestamp(ctime).strftime("%H:%M")
                date_str = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")
                curr_date_str = datetime.now().strftime("%Y-%m-%d")

                msg = f"<b>{file.split(".")[0]}</b> at {time_str}"

                if date_str != curr_date_str:
                    msg += f" ({date_str}):"
                else:
                    msg += ":"

                try:
                    with open(os.path.join(noti_path, file), "r", encoding="utf-8") as f:
                        msg += f"\n{f.read()}"

                    if store:
                        old_dir = os.path.join(noti_path, "old")

                        if not os.path.exists(old_dir):
                            os.makedirs(old_dir)

                        new_file_name = f"{file.split('.')[0]}_{int(time.time())}"
                        os.rename(os.path.join(noti_path, file),
                                  os.path.join(old_dir, new_file_name))
                    else:
                        os.remove(os.path.join(noti_path, file))

                except Exception as e:
                    logging.error(
                        "[%s] Unable to read the msg: [%s] - %s", file, type(e).__name__, str(e))

                    error_dir = os.path.join(noti_path, "errors")
                    if not os.path.exists(error_dir):
                        os.makedirs(error_dir)

                    os.rename(os.path.join(noti_path, file),
                              os.path.join(error_dir, file))

                    msg += (f"\nUnable to read the msg: {type(e).__name__}"
                            + f"\n{str(e)}")

                await context.bot.send_message(chat_id=os.getenv("CHAT_ID"),
                                               text=msg,
                                               parse_mode="HTML")

                logging.debug("[%s] Notification sent", file)

                time.sleep(5)

        except Exception as e:
            logging.error("Unable to get the notifications: [%s] - %s",
                          type(e).__name__, str(e))
