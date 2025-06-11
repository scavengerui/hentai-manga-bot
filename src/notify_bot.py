from telegram import Bot

def send_failure_alert(bot_token, chat_id, title, chapter_number, error_message):
    bot = Bot(token=bot_token)
    message = (
        f"⚠️ *Failed Upload Alert*\n\n"
        f"*Title:* {title}\n"
        f"*Chapter:* {chapter_number}\n"
        f"*Error:* `{error_message}`"
    )

    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")
