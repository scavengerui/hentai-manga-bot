import os
from telegram import Bot

def send_pdf_to_telegram(pdf_path, bot_token, chat_id, title, chapter):
    """
    Sends the generated PDF to the specified Telegram chat/channel.
    """
    bot = Bot(token=bot_token)

    caption = f"📖 *{title}* - Chapter {chapter}"
    try:
        with open(pdf_path, "rb") as f:
            bot.send_document(
                chat_id=chat_id,
                document=f,
                filename=os.path.basename(pdf_path),
                caption=caption,
                parse_mode="Markdown",
                timeout=120
            )
        print(f"✅ Sent to Telegram: {title} Chapter {chapter}")
    except Exception as e:
        print(f"❌ Failed to send to Telegram: {e}")
        raise
