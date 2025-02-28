# Server Telegram Bot

It provides system information and incorporates a simple notification system from other scripts.

## Table of Contents

- [Server Telegram Bot](#server-telegram-bot)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Usage](#usage)
    - [Environment variables](#environment-variables)
    - [Run](#run)
    - [Use with cron](#use-with-cron)
    - [Notifications](#notifications)
    - [Commands available in chat](#commands-available-in-chat)
      - [```/reboot```](#reboot)
        - [Example](#example)
      - [```/status```](#status)
        - [Example](#example-1)
  - [How-To](#how-to)
    - [Obtain your bot token](#obtain-your-bot-token)
    - [Obtain your user id](#obtain-your-user-id)
    - [Set command list in the bot](#set-command-list-in-the-bot)

## Requirements

1. Clone the project to your server.

    ```shell
    git clone https://github.com/javierorp/server-telegram-bot.git && cd server-telegram-bot && mv "[.]env" ".env"
    ```

2. Create a virtual environment.

    ```shell
    python -m venv .venv && source .venv/bin/activate
    ```

3. Install the required modules.

    ```shell
    pip install -r requirements.txt
    ```

4. Set the environment variables of the ".env" file (see [Environment variables](#environment-variables)).

## Usage

### Environment variables

The environment variables are required to work and are located in the ".env" file.

These are:

- **BOT_TOKEN:** Bot ID (see [Obtain your bot token](#obtain-your-bot-token)).
- **CHAT_ID:** User ID (see [Obtain your user id](#obtain-your-user-id)).
- **STORAGE_PATHS:** Absolute path of the storage devices to be displayed separated by commas.
- **NOTI_PATH:** Absolute path where the notifications will be stored. These notifications are simple files (UTF-8 encoding) with text inside.

### Run

To run the script by command:

```shell
~$ python main.py --help
usage: main.py [-h] [--hello] [--noti] [--save-noti] [-t TIME]

It provides system information and incorporates a simple notification system from other scripts.

options:
  -h, --help            show this help message and exit
  --hello               Send a message when the bot starts.
  --noti                Enable the notification check.
  --save-noti           Notifications are not deleted after sending. They are stored in a 'old' folder inside NOTI_PATH.
  -t TIME, --time TIME  Time in seconds to check new notifications to be sent. Default 10.
```

### Use with cron

Run the bot at server startup.

Open the crontab

```shell
~$ sudo crontab -e
```

and add next line modifying with the correct path in your case:

```shell
@reboot sleep 40; /home/user/server-telegram-bot/.venv/bin/python3 /home/user/server-telegram-bot/main.py --hello --noti  -t 60
```

### Notifications

It checks the files in NOTI_PATH, reads their content and sends, for each one of them, a message with the file name (app/script where the message comes from), the creation time and the content.

The file, depending on the configuration, would be deleted after the message is sent or moved to the "old" folder inside NOTI_PATH. If there is an error reading the file, the error message is sent and the file is moved to the "errors" folder inside NOTI_PATH.

For example, for the file "app_A" with the content "It's a text", the message would be:

```text
app_A at 14:12:
It's a text
```

### Commands available in chat

#### ```/reboot```

Reboot the server asking for user confirmation (Yes/No)

##### Example

```text
Rebooting the system... 🔄
```

#### ```/status```

Displays system information

##### Example

Example of the ```/status``` command.

```text
--------------- ℹ️ Info ---------------
Date & time: 2025-02-28 13:32:00
Uptime: 1 days 4 hours 20 min 30 sec
Package(s): 69 upgradable(s)

--------------- 🔲 CPU ---------------
Cores: 8
Frequency: 2969.754 MHz
Scaling governor: powersave
Load: 
     1 min: 0.68
     5 min: 0.78
     15 min: 0.78
Temperature: 35.05°C

--------------- 💾 RAM ---------------
RAM: 6.94 GB of 15.35 GB (58.0%) used

--------------- 🌐 Netwotk ---------------
Public IPv4: x.x.x.x
Public IPv6: xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx
Ethernet:
     Sent: 0.16 GB
     Received: 0.95 GB

--------------- 💽 Disk ---------------
root (/): 
     Used: 61.35 GB (22.38%)
     Free: 198.80 GB
     Total: 274.15 GB

--------------- 📂 Storage ---------------
MyDisk: 
     Used: 0.00 GB (0.00%)
     Free: 29.70 GB
     Total: 29.70 GB
```

## How-To

### Obtain your bot token

Contact [@BotFather](https://t.me/botfather) issuing the ```/newbot``` command and following the steps until you're given a new token. You can find a step-by-step guide [here](https://core.telegram.org/bots/features#creating-a-new-bot).

### Obtain your user id

Contact [@userinfobot](https://telegram.me/userinfobot) issuing the ```/start``` command to obtain your ID.

### Set command list in the bot

Contact [@BotFather](https://t.me/botfather) issuing the ```/setcommands``` command. Select your bot and send the following message.

```text
status - Displays server information.
reboot - Reboot the server.
```
