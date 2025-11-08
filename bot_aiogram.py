#!/usr/bin/env python3
"""
Strange Things Bot - Game (aiogram)
Place your real BOT_TOKEN in environment variable BOT_TOKEN (or use .env with python-dotenv).
This is a demo spooky-quiz game using in-memory state (for demo only).
"""

import os
import logging
import random
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import TelegramAPIError

# Load .env if present
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
if BOT_TOKEN == "your_bot_token_here":
    # The bot will still run but won't be able to perform API calls without a real token.
    logging.warning("BOT_TOKEN is placeholder. Set BOT_TOKEN environment variable to your real token before deploying.")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

SHORT_DESC = "Step into the Upside Down. 🎮 Face the strange, solve the mystery, and survive the night with Strange Things Bot."
LONG_DESC  = (
    "Welcome to Strange Things Bot — solve eerie puzzles, unlock clues, and uncover the secrets of Hawkins. "
    "Use /play to start the spooky quiz. Good luck..."
)

# Simple in-memory user state
user_state = {}  # user_id -> {"score": int, "qidx": int}

QUESTIONS = [
    {
        "q": "A static radio hums a number: 77. What do you do?",
        "choices": ["Ignore it", "Tune to frequency 77.7", "Smash the radio", "Record it"],
        "answer_index": 1,
        "hint": "Some frequencies like to repeat..."
    },
    {
        "q": "Three doors: one marked with a triangle, one with a circle, one with a square. Which opens?",
        "choices": ["Triangle", "Circle", "Square"],
        "answer_index": 2,
        "hint": "Think about corners vs curves."
    },
    {
        "q": "A whisper says: 'Reverse 1223 then add 1'. What is the result?",
        "choices": ["3222", "3224", "3223", "1233"],
        "answer_index": 1,
        "hint": "Reverse first, then math."
    },
    {
        "q": "You find a torn map with three X's. Which X glows faintly?",
        "choices": ["Top-left", "Center", "Bottom-right"],
        "answer_index": 2,
        "hint": "When in doubt, follow the corner."
    }
]

def question_kb(qidx):
    q = QUESTIONS[qidx]
    keyboard = types.InlineKeyboardMarkup()
    for i, choice in enumerate(q["choices"]):
        keyboard.add(types.InlineKeyboardButton(text=choice, callback_data=f"answer|{qidx}|{i}"))
    keyboard.add(types.InlineKeyboardButton(text="Get Hint", callback_data=f"hint|{qidx}"))
    keyboard.add(types.InlineKeyboardButton(text="Quit Game", callback_data="quit"))
    return keyboard

@dp.message_handler(commands=["start","help"])
async def cmd_start(message: types.Message):
    txt = (
        "👁️ Welcome to Strange Things Bot — the Upside Down quiz.\n\n"
        "Commands:\n"
        "/play - Start a spooky round\n"
        "/score - Show your score\n"
        "/quit - Quit the current game\n\n"
        "Be brave. Or be gone."
    )
    await message.reply(txt)

@dp.message_handler(commands=["play"])
async def cmd_play(message: types.Message):
    user = message.from_user.id
    qidx = random.randrange(len(QUESTIONS))
    user_state[user] = {"score": 0, "qidx": qidx}
    q = QUESTIONS[qidx]
    await message.reply(f"🕹️ {q['q']}", reply_markup=question_kb(qidx))

@dp.message_handler(commands=["score"])
async def cmd_score(message: types.Message):
    user = message.from_user.id
    st = user_state.get(user, {"score": 0})
    await message.reply(f"🏆 Your score: {st['score']}")

@dp.message_handler(commands=["quit"])
async def cmd_quit(message: types.Message):
    user = message.from_user.id
    if user in user_state:
        del user_state[user]
        await message.reply("🕯️ You have left the game. Come back if you dare.")
    else:
        await message.reply("No active game. Use /play to begin.")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("answer|"))
async def process_answer(call: types.CallbackQuery):
    _, qidx_s, choice_s = call.data.split("|")
    qidx = int(qidx_s); choice = int(choice_s)
    user = call.from_user.id
    q = QUESTIONS[qidx]
    st = user_state.setdefault(user, {"score": 0, "qidx": None})
    correct = (choice == q["answer_index"])
    if correct:
        st["score"] += 10
        text = "✅ Correct! +10 points."
    else:
        st["score"] -= 5
        text = f"❌ Wrong. -5 points. Hint: {q['hint']}"
    # choose next question
    next_qidx = random.randrange(len(QUESTIONS))
    st["qidx"] = next_qidx
    try:
        await call.answer(text, show_alert=True)
        await call.message.edit_text(f"{text}\n\nNext: {QUESTIONS[next_qidx]['q']}", reply_markup=question_kb(next_qidx))
    except Exception:
        # fallback: send new message
        await call.message.reply(f"{text}\n\nNext: {QUESTIONS[next_qidx]['q']}", reply_markup=question_kb(next_qidx))

@dp.callback_query_handler(lambda c: c.data == "quit")
async def process_quit(call: types.CallbackQuery):
    user = call.from_user.id
    if user in user_state:
        del user_state[user]
    await call.answer("Game ended. Goodbye.", show_alert=True)
    await call.message.edit_text("🕯️ Game ended. Use /play to start again.")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("hint|"))
async def process_hint(call: types.CallbackQuery):
    _, qidx_s = call.data.split("|")
    qidx = int(qidx_s)
    q = QUESTIONS[qidx]
    await call.answer(f"💡 Hint: {q['hint']}", show_alert=True)

async def set_bot_texts():
    try:
        await bot.set_my_short_description(short_description=SHORT_DESC)
        await bot.set_my_description(description=LONG_DESC)
        logging.info("Set short and long descriptions.")
    except TelegramAPIError as e:
        logging.warning("Could not set bot descriptions: %s", e)

async def on_startup(dp):
    await set_bot_texts()
    logging.info("Bot started (on_startup complete).")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
