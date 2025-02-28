# pylint: disable=unused-argument
"""System information"""

from datetime import datetime
import os
import shutil
import subprocess
import time
import psutil
import requests
from telegram import Update
from telegram.ext import ContextTypes


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the status of the system"""

    # ---- Info ----
    def get_current_datetime():
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def format_uptime(seconds):
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{days} days {hours} hours {minutes:02} min {secs:02} sec"

    def get_uptime():
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            return format_uptime(int(uptime_seconds))
        except:
            try:
                with open("/proc/uptime", "r", encoding="utf-8") as f:
                    uptime_seconds = float(f.readline().split()[0])
                return format_uptime(int(uptime_seconds))
            except:
                return "Unknown"

    def get_upgradable_packages():
        try:
            output = subprocess.check_output(
                ["apt", "list", "--upgradable"]).decode()
            lines = output.strip().split("\n")
            return len(lines) - 1 if len(lines) > 1 else 0
        except:
            return "Unknown"

    # ---- CPU ----
    def get_cpu_frequency():
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "r", encoding="utf-8") as f:
                freq = int(f.read().strip()) / 1000  # MHz
            return f"{freq} MHz"
        except:
            return "Unknown"

    def get_voltage():
        try:
            output = subprocess.check_output(
                ["vcgencmd", "measure_volts", "core"]).decode()
            return output.strip().replace("volt=", "")
        except:
            return "Unknown"

    def get_scaling_governor():
        try:
            with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            return "Unknown"

    def get_cpu_load():
        try:
            load_1, load_5, load_15 = os.getloadavg()
            return f"\n     1 min: {round(load_1, 2)}\n     5 min: {round(load_5, 2)}\n     15 min: {round(load_15, 2)}"
        except:
            return "Unknown"

    def get_cpu_temperature():
        try:
            output = subprocess.check_output(
                ["vcgencmd", "measure_temp"]).decode()
            return output.strip().replace("temp=", "").replace("'C", "°C")
        except:
            try:
                with open("/sys/class/thermal/thermal_zone0/temp", "r", encoding="utf-8") as f:
                    temp = int(f.read().strip()) / 1000  # Convertir a °C
                return f"{temp}°C"
            except:
                return "Unknown"

    # ---- RAM ----
    def get_ram():
        try:
            memory = psutil.virtual_memory()
            total = memory.total / (1024 ** 3)
            used = memory.used / (1024 ** 3)
            percent = memory.percent

            return f"{used:.2f} GB of {total:.2f} GB ({percent}%)"
        except:
            return "Unknown"

    # ---- Network ----
    def get_public_ipv4():
        try:
            response = requests.get(
                "https://api.ipify.org?format=json", timeout=30)
            return response.json().get('ip')
        except:
            return "-"

    def get_public_ipv6():
        try:
            response = requests.get(
                "https://api64.ipify.org?format=json", timeout=30)
            return response.json().get('ip')
        except:
            return "-"

    def get_network_stats():
        stats = psutil.net_io_counters()
        sent_gb = stats.bytes_sent / (1024 ** 3)
        recv_gb = stats.bytes_recv / (1024 ** 3)
        return sent_gb, recv_gb

    # ---- Disk / Storage ----
    def get_storage_info(directory="", mb=False):
        try:
            mult = 3 if not mb else 2
            size_f = "MB" if mb else "GB"
            total, used, free = shutil.disk_usage(directory)

            total_mb = total / (1024 ** mult)
            used_mb = used / (1024 ** mult)
            free_mb = free / (1024 ** mult)

            perc_used = (used / total) * 100

            return (
                f"\n     Used: {used_mb:.2f} {size_f} ({perc_used:.2f}%)\n"
                + f"     Free: {free_mb:.2f} {size_f}\n     Total: {total_mb:.2f} {size_f}")
        except:
            return "Unknown"

    # ---- Data ----
    sent, received = get_network_stats()

    data = (
        "--------------- ℹ️ <b>Info</b> ---------------\n"
        f"<b>Date & time:</b> {get_current_datetime()}\n"
        f"<b>Uptime:</b> {get_uptime()}\n"
        f"<b>Package(s):</b> {get_upgradable_packages()} upgradable(s)\n"
        "\n--------------- 🔲 <b>CPU</b> ---------------\n"
        f"<b>Cores:</b> {os.cpu_count()}\n"
        f"<b>Frequency:</b> {get_cpu_frequency()}\n")

    volts = get_voltage()
    if volts != "Unknown":
        data += f"<b>Voltage:</b> {get_voltage()}\n"

    data += (
        f"<b>Scaling governor:</b> {get_scaling_governor()}\n"
        f"<b>Load:</b> {get_cpu_load()}\n"
        f"<b>Temperature:</b> {get_cpu_temperature()}\n"
        "\n--------------- 💾 <b>RAM</b> ---------------\n"
        f"<b>RAM:</b> {get_ram()} used\n"
        "\n--------------- 🌐 <b>Netwotk</b> ---------------\n"
        f"<b>Public IPv4:</b> {get_public_ipv4()}\n"
        f"<b>Public IPv6:</b> {get_public_ipv6()}\n"
        f"<b>Ethernet:</b>\n"
        f"     Sent: {sent:.2f} GB\n"
        f"     Received: {received:.2f} GB\n"
    )

    data += "\n--------------- 💽 <b>Disk</b> ---------------\n"
    boot_fw = get_storage_info("/boot/firmware", mb=True)
    if boot_fw != "Unknown":
        data += f"<b>/boot/firmware:</b> {get_storage_info("/boot/firmware", mb=True)}\n"

    data += f"<b>root (/):</b> {get_storage_info("/")}\n"

    storage_paths = os.getenv("STORAGE_PATHS")
    if storage_paths:
        data += "\n--------------- 📂 <b>Storage</b> ---------------\n"
        for path in storage_paths.split(","):
            name = os.path.basename(os.path.normpath(path))
            data += f"<b>{name}:</b> {get_storage_info(path)}\n"

    await context.bot.send_message(chat_id=os.getenv("CHAT_ID"), text=data, parse_mode="HTML")
