# 🧹 Message Cleaner

**Message Cleaner** is a powerful and customizable Discord bot manager that automatically deletes messages older than a specified time in selected channels. Designed with a modern GUI, auto-updater, and system tray support — it's ideal for keeping your server clean and organized.

![GUI Preview](https://media.discordapp.net/attachments/1388905295480361063/1388905894057611507/message-cleaner-gui-preview.PNG?ex=6862aee9&is=68615d69&hm=85699c9be0e2e1893e2e2c649393b52f83fb7d9cfb21ee131e541d3c8ea08af0&=&format=webp&quality=lossless)

---

## 📦 Features

- ✅ **GUI Interface** – No need to use command line or edit code
- 🔄 **Auto Cleanup** – Deletes old messages on a timed interval
- 🗂️ **Multi-Channel Support** – Specify multiple channels
- 🛠️ **Configurable Settings** – Token, interval, age, and channels
- 📜 **Log Viewer** – View/delete log files directly from the app
- 🚨 **Update Checker** – Automatically notifies users of new versions
- 🧊 **Minimize to Tray** – Runs quietly in the background

---

## 📂 Download

👉 Get the latest release from the [official Discord thread](https://discord.com/channels/1295360135463567511/1388437655787929685)  
🖱️ Just run the `.exe` — no installation needed!

> If you're a developer or advanced user, you can also clone and run the source code using Python 3.10+.

---

## ⚙️ Usage (Executable)

1. **Run** the `.exe` file
2. **Enter your settings**:
   - Your bot's token
   - Channel IDs (comma-separated)
   - Delete messages older than (in minutes)
   - Check interval (in seconds)
3. Click **Save & Start**
4. Monitor real-time logs and minimize to tray if needed

Configuration and logs are saved to:
C:\Users<YourName>\Documents\Random Python\Message Cleaner\



---

## 🛡️ Security & Token Notice

⚠️ **Important:** The `update_checker` bot token is hardcoded in the executable version to fetch version info via Discord.

> The source code version has this token **redacted** for security reasons.  
> The token is restricted to a single read-only channel and **cannot be misused**.

Your own bot token (used for cleaning) is stored in your local config file and **never shared**.

---

## 👨‍💻 Developers

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
python message_cleaner_gui.py
To build the executable using PyInstaller:


pyinstaller --onefile --noconsole --icon=Cleaner_icon-icons.com_53211.ico --add-data "Cleaner_icon-icons.com_53211.ico;." message_cleaner_gui.py
📜 License
Message Cleaner is released under a custom license.

You may use, modify, and distribute the code

You must not monetize it or use it for malicious/illegal purposes

You must give credit and notify users of unofficial changes

See LICENSE.txt for full terms.

✨ Credits
Made by the Random Python Discord
Join us for help, suggestions, or fun projects:
https://discord.gg/AEVnNyDZj7
