# Strange Things Bot (Spooky Quiz)

This is a ready-to-deploy Telegram bot (aiogram) that runs a spooky quiz game.
Put your real `BOT_TOKEN` in an environment variable when deploying (do NOT commit secrets).

## Files
- `bot_aiogram.py` - main bot code (game with inline buttons)
- `requirements.txt` - Python dependencies
- `.env.example` - placeholder for BOT_TOKEN
- `README.md` - this file

## Local testing
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` and add your real bot token:
   ```
   BOT_TOKEN=123456:ABC-DEF...
   ```
4. Run:
   ```bash
   python bot_aiogram.py
   ```
5. Open Telegram, search your bot, and send `/start`.

## Deploy to Render (recommended)
1. Push this project to a GitHub repository.
2. Create a **Background Worker** on Render and connect to the repo.
3. Set the start command to:
   ```
   python bot_aiogram.py
   ```
4. Add an environment variable on Render:
   - Key: `BOT_TOKEN`
   - Value: *your BotFather token*
5. Deploy. Check logs for a "Bot started" message.

## Security notes
- Never share your bot token publicly.
- For production, use a persistent database (SQLite / Redis) instead of in-memory state.
