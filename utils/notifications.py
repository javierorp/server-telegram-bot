"""Notifications"""

import os
import time
from datetime import datetime
from telegram.ext import ContextTypes


async def get_notifications(context: ContextTypes.DEFAULT_TYPE):
    """Check the notifications and send them to the chat"""

    store = context.job.data.get("store", True)

    noti_path = os.getenv("NOTI_PATH")
    if noti_path:
        files = [f for f in os.listdir(
            noti_path) if os.path.isfile(os.path.join(noti_path, f))]
        files_with_dates = [(file, os.path.getctime(
            os.path.join(noti_path, file))) for file in files]

        files_with_dates.sort(key=lambda x: x[1])

        for file, ctime in files_with_dates:
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

            except Exception as e:  # pylint: disable=broad-except
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

            time.sleep(5)
