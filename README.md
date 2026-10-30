# PySoroush

A modern, simple, and powerful Python library for the **Soroush Plus** messenger.

Designed with an intuitive API so that even beginners can build bots and user-automation scripts with just a few lines of code.

[![PyPI version](https://img.shields.io/pypi/v/pysoroush.svg)](https://pypi.org/project/pysoroush/)
[![Python versions](https://img.shields.io/pypi/pyversions/pysoroush.svg)](https://pypi.org/project/pysoroush/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

### Bot API (Synchronous & Asynchronous)
- Full support for the official Soroush Plus Bot API.
- Both **Sync** (`requests`) and **Async** (`aiohttp`) clients.
- **Auto-Retry** with exponential backoff on network failures.
- **Rate Limit** handling (automatic sleeping when hitting 429).
- **Fluent Keyboard Builder** for building complex keyboards easily.
- **Filters** for routing messages (`Text`, `Photo`, `Private`, `StateFilter`, etc.).
- **FSM (Finite State Machine)** for multi-step conversations.
- **Media** support (photos, videos, documents, audio, media groups).
- **WebApp** data validation (HMAC-SHA-256).

### Account API (Self / Userbot) - 100% Independent Engine
Powered by an **embedded custom MTProto engine**, written from scratch for this project. 
There are **no third-party Soroush wrappers** required. It's fully independent and optimized for Soroush Plus.

- Login with phone number + OTP (Two-Step Verification supported).
- Send and receive text messages, polls, locations, and contacts.
- Read history, edit, delete, forward, and react to messages.
- Group and channel management (create, leave, archive, mute, block).
- Folder management (create, edit, delete).
- Raw TL API access for advanced use cases.
- 9 Event handlers (`on_message`, `on_callback`, `on_edited_message`, etc.).
- Sync and Async interfaces.

> **Note on Server Limitations**: Due to Soroush Plus's server restrictions over WebSockets, certain features like **uploading files** (photos/documents), **clearing chat history**, and **exporting invite links** are not supported by the server. The library handles these gracefully.

---

## Installation

```bash
pip install pysoroush
```

---

Quick Start

1. Bot API (Simple Polling)

```python
from pysoroush.bot import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.command("start")
def start_handler(msg):
    return bot.reply(msg, "Hello! I am a bot.")

@bot.on_message()
def echo_handler(msg):
    bot.reply(msg, f"You said: {msg.text}")
    return True

bot.run()  # Start polling
```

2. Account API (Userbot)

```python
import asyncio
from pysoroush.account import AsyncClient

async def main():
    # The first run will prompt for phone number and OTP
    async with AsyncClient(session_file="my_account") as client:
        if not await client.is_authorized():
            phone = input("Phone number (e.g., 989123456789): ")
            await client.start(phone=phone, code_callback=lambda: input("OTP: "))

        me = await client.get_me()
        print(f"Logged in as {me.first_name}")

        # Send a message to yourself
        await client.send_message("me", "Hello from my own account!")

        # List dialogs
        dialogs = await client.get_dialogs(limit=10)
        for dialog in dialogs:
            print(f"- {dialog.name}")

asyncio.run(main())
```

3. Account API with Event Handlers

```python
import asyncio
from pysoroush.account import AsyncClient

async def main():
    async with AsyncClient(session_file="my_account") as client:
        if not await client.is_authorized():
            phone = input("Phone: ")
            await client.start(phone=phone, code_callback=lambda: input("OTP: "))

        @client.on_message()
        async def auto_reply(message):
            if message.text == "ping":
                await message.reply("pong!")

        print("Listening for messages...")
        await client.run_until_disconnected()

asyncio.run(main())
```

---

Security Notes

· Never commit your *.session files to GitHub. These files contain your authentication tokens.
· The Account API is based on the MTProto protocol and is provided for automation purposes only. Please respect Soroush Plus's Terms of Service.

---

License

This project is licensed under the MIT License.
See the LICENSE file for details.

---

Author

Ali VEX

· GitHub: @lyrdaadhrpyk802-ux
  PYEOF
  echo "Updated: README.md with new 0.2.0 independent features."

```