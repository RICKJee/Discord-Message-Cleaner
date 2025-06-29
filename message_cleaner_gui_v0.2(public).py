import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import json
import asyncio
import datetime
import time
import sys
import os
import webbrowser
from pathlib import Path
import pystray
from pystray import MenuItem as item
from PIL import Image
import logging
import discord
from discord.ext import commands, tasks

CONFIG_DIR = Path.home() / "Documents/Random Python/Message Cleaner"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = CONFIG_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

APP_VERSION = "0.2"
DISCORD_BOT_TOKEN = "[REDACTED]"  # Replace with a secure bot token for update check
UPDATE_CHANNEL_ID = 1388447215017529404
UPDATE_MESSAGE_ID = 1388447503833235506
UPDATE_THREAD_URL = "https://discord.com/channels/1295360135463567511/1388437655787929685"

log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_path = LOG_DIR / log_filename
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(message)s')

bot_thread = None
bot_loop = None
bot_instance = None
tray_icon = None
window = None

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TextRedirector:
    def __init__(self, widget):
        self.widget = widget
    def write(self, string):
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)
        self.widget.configure(state="disabled")
        logging.info(string.strip())
    def flush(self):
        pass

async def fetch_latest_update():
    intents = discord.Intents.default()
    intents.guilds = True
    intents.message_content = True

    class UpdateChecker(discord.Client):
        async def on_ready(self):
            try:
                channel = await self.fetch_channel(UPDATE_CHANNEL_ID)
                message = await channel.fetch_message(UPDATE_MESSAGE_ID)
                lines = message.content.splitlines()
                version_line = next((line for line in lines if line.lower().startswith("current version:")), None)
                changelog_lines = [line for line in lines if line.lower().startswith("update info:") or line.startswith("-")]
                if version_line:
                    latest_version = version_line.split(":", 1)[1].strip()
                    if latest_version > APP_VERSION:
                        changelog = "\n".join(changelog_lines)
                        prompt_update(latest_version, UPDATE_THREAD_URL, changelog)
                    else:
                        print(f"✔ You're running the latest version ({APP_VERSION}).")
                else:
                    print("⚠ Couldn't find version info in update message.")
            except Exception as e:
                print(f"❌ Failed to check for updates: {e}")
            await self.close()

    client = UpdateChecker(intents=intents)
    await client.start(DISCORD_BOT_TOKEN)

def check_for_updates():
    threading.Thread(target=lambda: asyncio.run(fetch_latest_update()), daemon=True).start()

def prompt_update(version, url, changelog):
    if messagebox.askyesno("Update Available", f"Version {version} is available!\n\nChangelog:\n{changelog}\n\nOpen download thread?"):
        if url:
            webbrowser.open(url)

def run_bot():
    global bot_loop, bot_instance
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config.json: {e}")
        return

    TOKEN = config['token']
    CHANNEL_IDS = config['channel_ids']
    DELETE_AGE = config['delete_older_than_minutes']
    INTERVAL = config['check_interval_seconds']

    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    bot_instance = bot
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)

    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        delete_old_messages.start()

    @tasks.loop(seconds=INTERVAL)
    async def delete_old_messages():
        now = datetime.datetime.now(datetime.timezone.utc)
        threshold = now - datetime.timedelta(minutes=DELETE_AGE)
        for channel_id in CHANNEL_IDS:
            channel = bot.get_channel(channel_id)
            if not isinstance(channel, discord.TextChannel):
                continue
            print(f"🔍 Checking: {channel.name}")
            try:
                async for message in channel.history(limit=500):
                    if message.created_at < threshold:
                        try:
                            await message.delete()
                            print(f"🗑️ Deleted message from {message.author}")
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"❌ Failed to delete: {e}")
            except Exception as e:
                print(f"⚠️ Error with channel {channel_id}: {e}")

    try:
        bot_loop.run_until_complete(bot.start(TOKEN))
    except Exception as e:
        print(f"💥 Bot crash: {e}")
    finally:
        bot_loop.run_until_complete(bot.close())

def start_bot():
    global bot_thread
    if bot_thread and bot_thread.is_alive():
        print("⚠️ Bot already running.")
        return
    print("🚀 Starting bot...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

def stop_bot():
    if bot_loop and bot_loop.is_running():
        print("🛑 Stopping bot...")
        bot_loop.call_soon_threadsafe(lambda: asyncio.create_task(bot_instance.close()))
    else:
        print("⚠️ Bot not running.")

def restart_bot():
    stop_bot()
    time.sleep(2)
    start_bot()

def delete_logs():
    if messagebox.askyesno("Delete Logs", "Are you sure you want to delete all logs?"):
        for file in LOG_DIR.glob("*.log"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Failed to delete {file.name}: {e}")
        print("🗑️ All logs deleted.")

def save_config():
    try:
        token = token_entry.get().strip()
        channels = list(map(int, channel_entry.get().split(',')))
        age = int(age_entry.get())
        interval = int(interval_entry.get())
        config = {
            "token": token,
            "channel_ids": channels,
            "delete_older_than_minutes": age,
            "check_interval_seconds": interval
        }
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("💾 Config saved.")
        return True
    except Exception as e:
        messagebox.showerror("Invalid Input", f"Error: {e}")
        return False

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            token_entry.insert(0, config.get("token", ""))
            channel_entry.insert(0, ",".join(map(str, config.get("channel_ids", []))))
            age_entry.delete(0, tk.END)
            age_entry.insert(0, str(config.get("delete_older_than_minutes", 60)))
            interval_entry.delete(0, tk.END)
            interval_entry.insert(0, str(config.get("check_interval_seconds", 1800)))
            print("📂 Loaded saved config.")
        except Exception as e:
            print(f"⚠️ Failed to load saved config: {e}")

def save_and_start():
    if save_config():
        start_bot()

def show_about():
    about = tk.Toplevel(window)
    about.title("About")
    about.geometry("350x250")
    about.configure(bg="#2f3136")
    tk.Label(about, text=f"Message Cleaner v{APP_VERSION}\n\nMade by Random Python Discord", bg="#2f3136", fg="white", font=("Segoe UI", 11)).pack(pady=15)
    tk.Button(about, text="Join Discord Server", command=lambda: webbrowser.open("https://discord.gg/AEVnNyDZj7"), bg="#5865F2", fg="white").pack(pady=5)
    tk.Button(about, text="Check for Updates", command=check_for_updates, bg="#4f545c", fg="white").pack(pady=5)
    tk.Button(about, text="Close", command=about.destroy, bg="#4f545c", fg="white").pack(pady=5)

def create_gui():
    global window, token_entry, channel_entry, age_entry, interval_entry
    window = tk.Tk()
    window.title(f"Message Cleaner v{APP_VERSION}")
    window.geometry("700x620")
    window.configure(bg="#2f3136")

    def styled_label(text):
        return tk.Label(window, text=text, bg="#2f3136", fg="#dcddde", font=("Segoe UI", 10))

    styled_label("Bot Token:").pack()
    token_entry = tk.Entry(window, width=80, bg="#202225", fg="white")
    token_entry.pack()

    styled_label("Channel IDs (comma-separated):").pack()
    channel_entry = tk.Entry(window, width=80, bg="#202225", fg="white")
    channel_entry.pack()

    styled_label("Delete Messages Older Than (minutes):").pack()
    age_entry = tk.Entry(window, width=20, bg="#202225", fg="white")
    age_entry.insert(0, "60")
    age_entry.pack()

    styled_label("Check Interval (seconds):").pack()
    interval_entry = tk.Entry(window, width=20, bg="#202225", fg="white")
    interval_entry.insert(0, "1800")
    interval_entry.pack()

    button_frame = tk.Frame(window, bg="#2f3136")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Save & Start", command=save_and_start, bg="#5865F2", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame, text="Stop Bot", command=stop_bot, bg="#ED4245", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame, text="Restart Bot", command=restart_bot, bg="#FEE75C", fg="black").pack(side='left', padx=5)
    tk.Button(button_frame, text="Open Logs Folder", command=lambda: os.startfile(LOG_DIR), bg="#4f545c", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame, text="Delete All Logs", command=delete_logs, bg="#4f545c", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame, text="About", command=show_about, bg="#4f545c", fg="white").pack(side='left', padx=5)

    log_box = scrolledtext.ScrolledText(window, state='disabled', wrap='word', bg='#202225', fg='lime', font=('Consolas', 10))
    log_box.pack(expand=True, fill='both', padx=10, pady=10)
    sys.stdout = TextRedirector(log_box)

    load_config()
    check_for_updates()
    window.mainloop()

if __name__ == "__main__":
    create_gui()
