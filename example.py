"""
Comprehensive test script for PySoroush.
"""

from pysoroush.bot import Bot
from pysoroush.bot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, InputFile
)
from pysoroush.bot.filters import Text, Photo, Document, StateFilter

# Replace with your actual token
bot = Bot(token="YOUR_BOT_TOKEN_HERE", debug=True)


@bot.command("start")
def start_command(msg, ctx):
    ctx.clear()
    inline_kb = InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="Test Callback 1", callback_data="cb_test_1"),
        InlineKeyboardButton(text="Test Callback 2", callback_data="cb_test_2")
    ).row(
        InlineKeyboardButton(text="Open Soroush", url="https://splus.ir")
    )
    bot.reply(msg, "Welcome to PySoroush test bot!", reply_markup=inline_kb)
    return True


@bot.command("menu")
def menu_command(msg):
    reply_kb = ReplyKeyboardMarkup().row(
        "Button 1", "Button 2"
    ).row(
        "Start FSM Test"
    ).resize(True).one_time(False)
    bot.reply(msg, "Here is your custom keyboard.", reply_markup=reply_kb)
    return True


@bot.command("cancel")
def cancel_command(msg, ctx):
    ctx.clear()
    bot.reply(msg, "State cleared.")
    return True


@bot.on_message(Text("Start FSM Test"))
def trigger_fsm(msg, ctx):
    ctx.set_state("waiting_for_name")
    bot.reply(msg, "FSM Started! What is your name?")
    return True


@bot.on_message(StateFilter("waiting_for_name"))
def fsm_name_handler(msg, ctx):
    name = msg.text
    ctx.set_data("name", name)
    ctx.set_state("waiting_for_age")
    bot.reply(msg, f"Nice to meet you, {name}! How old are you?")
    return True


@bot.on_message(StateFilter("waiting_for_age"))
def fsm_age_handler(msg, ctx):
    age = msg.text
    name = ctx.get_data("name")
    ctx.clear()
    bot.reply(msg, f"Thank you! You are {name} and you are {age} years old. FSM completed!")
    return True


@bot.on_callback()
def handle_callback(callback):
    if callback.data == "cb_test_1":
        bot.answer_callback_query(callback.id, text="You clicked button 1!", show_alert=True)
        bot.edit_message_text(
            text="You clicked Button 1. Edited successfully!",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )
    elif callback.data == "cb_test_2":
        bot.answer_callback_query(callback.id, text="You clicked button 2!")
        bot.edit_message_text(
            text="You clicked Button 2. Edited successfully!",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )
    else:
        bot.answer_callback_query(callback.id)
    return True


@bot.on_message(Photo())
def handle_photo(msg):
    largest_photo = msg.photo[-1]
    bot.reply(msg, f"I received your photo! file_id: {largest_photo.file_id}")
    bot.send_photo(chat_id=msg.chat.id, photo=largest_photo.file_id, caption="Here is your photo back.")
    return True


@bot.on_message(Document())
def handle_document(msg):
    doc = msg.document
    bot.reply(msg, f"Document received!\nName: {doc.file_name}\nSize: {doc.file_size} bytes")
    return True


@bot.on_message()
def echo_handler(msg, ctx):
    if ctx.state:
        return False
    bot.reply(msg, f"You said: {msg.text}")
    return True


if __name__ == "__main__":
    print("Starting test bot...")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Bot stopped.")
