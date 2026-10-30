# PySoroush

A modern, simple, and powerful Python library for the Soroush Plus messenger.

Designed with an intuitive API so that even beginners can build bots and user-automation scripts with just a few lines of code.

[![PyPI version](https://img.shields.io/pypi/v/pysoroush.svg)](https://pypi.org/project/pysoroush/)
[![Python versions](https://img.shields.io/pypi/pyversions/pysoroush.svg)](https://pypi.org/project/pysoroush/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

### Bot API (Synchronous & Asynchronous)
- Full support for the official Soroush Plus Bot API
- Both Sync (requests) and Async (aiohttp) clients
- Auto-Retry with exponential backoff on network failures
- Rate Limit handling (automatic sleeping when hitting 429)
- Fluent Keyboard Builder for building complex keyboards easily
- Filters for routing messages (Text, Photo, Private, StateFilter, etc.)
- FSM (Finite State Machine) for multi-step conversations
- Media support (photos, videos, documents, audio, media groups)
- WebApp data validation (HMAC-SHA-256)

### Account API (Self / Userbot)
- Login with phone number + OTP
- Two-Step Verification support
- Send and receive messages as your own user
- Send media (photos, files, etc.)
- Read message history, edit, delete, forward
- Download media
- Get dialogs and participants
- Event handlers (on_message, on_callback, on_edited_message, etc.)
- Raw TL API access for advanced use cases
- Sync and Async interfaces

---

## Installation

pip install pysoroush
---

Quick Start

1. Bot API (Simple Polling)

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
2. Bot API with Inline Keyboards

from pysoroush.bot import Bot
from pysoroush.bot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot("YOUR_BOT_TOKEN")

@bot.command("menu")
def menu_handler(msg):
    kb = InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="Option 1", callback_data="opt1"),
        InlineKeyboardButton(text="Open Website", url="https://splus.ir")
    )
    bot.reply(msg, "Choose an option:", reply_markup=kb)
    return True

@bot.on_callback()
def handle_callback(callback):
    bot.answer_callback_query(callback.id, text=f"You clicked: {callback.data}")
    return True

bot.run()
3. Async Bot

import asyncio
from pysoroush.bot import AsyncBot

bot = AsyncBot("YOUR_BOT_TOKEN")

@bot.command("start")
async def start_handler(msg):
    await bot.reply(msg, "Hello async world!")
    return True

async def main():
    await bot.run()

asyncio.run(main())
4. Account API (Userbot)

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

        await client.send_message("me", "Hello from my own account!")
        await client.send_photo("me", "/path/to/photo.jpg", caption="Check this out!")

        dialogs = await client.get_dialogs(limit=10)
        for dialog in dialogs:
            print(f"- {dialog.name}")

asyncio.run(main())
5. Account API with Event Handlers

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
---

Security Notes

· Never commit your *.session files to GitHub. These files contain your authentication tokens.
· Use environment variables to store bot tokens in production.
· The Account API is based on the MTProto protocol and is provided for automation purposes only. Please respect Soroush Plus's Terms of Service.

---

Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check the issues page.

---

License

This project is licensed under the MIT License.
See the LICENSE file for details.

---

Author

Ali VEX

· GitHub: @lyrdaadhrpyk802-ux
· Email: lyrdaadhrpyk802@gmail.com