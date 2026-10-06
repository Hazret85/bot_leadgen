import os
import logging
import asyncio
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key.strip()] = val.strip()

from database import init_db, add_user, add_message, get_chat_history, clear_chat_history
from ai_agent import generate_reply

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TRACKING_LINK = os.getenv("TRACKING_LINK", "https://t.me/your_short_link_here")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await add_user(user.id, user.username)
    
    m1 = "Hi, I'm busy right now, give me a couple of minutes, I'll come back and tell you how you can work with me"
    await context.bot.send_message(chat_id=user.id, text=m1)
    await add_message(user.id, "assistant", m1)
    
    delay1 = random.uniform(10, 15)
    await context.bot.send_chat_action(chat_id=user.id, action='typing')
    await asyncio.sleep(delay1)
    
    m2 = "I'm here"
    await context.bot.send_message(chat_id=user.id, text=m2)
    await add_message(user.id, "assistant", m2)
    
    delay2 = random.uniform(3, 5)
    await context.bot.send_chat_action(chat_id=user.id, action='typing')
    await asyncio.sleep(delay2)
    
    m3 = "Do you want to start trading with me, or are you looking for something else?"
    await context.bot.send_message(chat_id=user.id, text=m3)
    await add_message(user.id, "assistant", m3)

async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await clear_chat_history(user.id)
    await context.bot.send_message(chat_id=user.id, text="[System] Memory cleared! Send /start to begin a new scenario.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_text = update.message.text
    
    await add_user(user.id, user.username)
    await add_message(user.id, "user", user_text)
    
    await context.bot.send_chat_action(chat_id=user.id, action='typing')
    
    history = await get_chat_history(user.id, limit=20)
    reply_text = await generate_reply(history)
    
    await add_message(user.id, "assistant", reply_text)
    
    send_tg = "[SEND_TG_SCREENSHOT]" in reply_text
    send_wa = "[SEND_WA_SCREENSHOT]" in reply_text
    send_fwd = "[SEND_FORWARDED_MESSAGE]" in reply_text
    send_link = "[SEND_TRACKING_LINK]" in reply_text
    
    clean_text = reply_text.replace("[SEND_TG_SCREENSHOT]", "") \
                           .replace("[SEND_WA_SCREENSHOT]", "") \
                           .replace("[SEND_FORWARDED_MESSAGE]", "") \
                           .replace("[SEND_TRACKING_LINK]", "").strip()
    
    if clean_text:
        messages = clean_text.split('\n\n')
        for msg in messages:
            if msg.strip():
                await context.bot.send_chat_action(chat_id=user.id, action='typing')
                await asyncio.sleep(random.uniform(1.5, 3.5))
                await context.bot.send_message(chat_id=user.id, text=msg.strip())
                
    if send_fwd:
        await asyncio.sleep(random.uniform(1, 2))
        await context.bot.send_message(
            chat_id=user.id, 
            text="*Forwarded Message*\n\nThanks bro last 10 signals made me 766$",
            parse_mode="Markdown"
        )
    if send_tg:
        await context.bot.send_chat_action(chat_id=user.id, action='upload_photo')
        await asyncio.sleep(random.uniform(1, 2))
        try:
            with open("assets/tg_proof.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=user.id, photo=photo)
        except FileNotFoundError:
            pass
    if send_wa:
        await context.bot.send_chat_action(chat_id=user.id, action='upload_photo')
        await asyncio.sleep(random.uniform(1, 2))
        try:
            with open("assets/wa_proof.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=user.id, photo=photo)
        except FileNotFoundError:
            pass
    if send_link:
        await asyncio.sleep(random.uniform(1, 2))
        await context.bot.send_message(chat_id=user.id, text=f"{TRACKING_LINK}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    
    bot_token = os.getenv("bot_token")
    if not bot_token:
        exit(1)
        
    app = ApplicationBuilder().token(bot_token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_chat))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
