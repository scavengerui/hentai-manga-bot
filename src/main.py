import os
import json
import time
import traceback

from scraper import scrape_image_urls
from converter import download_images, convert_images_to_pdf
from drive_utils import upload_pdf_to_drive
from telegram_utils import send_pdf_to_telegram
from notify_bot import send_failure_alert

CONFIG_PATH = "../config/hentai_config.json" 
PROGRESS_PATH = "../config/progress.json"

RETRY_LIMIT = 3

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    print("🚀 Starting HentaiBot...")
    config = load_json(CONFIG_PATH)
    progress = load_json(PROGRESS_PATH)

    if not config:
        print("❌ No config found. Check hentai_config.json!")
        return

    for title, data in config.items():
        base_url = data["base_url"]
        start_chapter = progress.get(title, 1)
        chat_id = data["telegram_chat_id"]
        bot_token = data["telegram_bot_token"]
        drive_folder = data["drive_folder_id"]
        alert_token = data.get("alert_bot_token")
        alert_chat_id = data.get("alert_chat_id")

        print(f"\n📚 Processing title: {title}")
        chapter = start_chapter

        while True:
            print(f"\n➡️ Starting Chapter {chapter}...")

            chapter_url = base_url.format(chapter)
            temp_dir = f"temp_{title.replace(' ', '_')}_{chapter}"
            os.makedirs(temp_dir, exist_ok=True)
            pdf_filename = f"{title} - Chapter {chapter}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)

            success = False

            for attempt in range(1, RETRY_LIMIT + 1):
                print(f"🔄 Attempt {attempt}/3")
                try:
                    print("🔍 Scraping image URLs...")
                    image_urls = scrape_image_urls(chapter_url)
                    if not image_urls:
                        raise Exception("No images found on the page.")

                    print("📥 Downloading images...")
                    image_paths = download_images(image_urls, temp_dir)
                    if not image_paths:
                        raise Exception("Image download failed.")

                    print("🧾 Converting to PDF...")
                    convert_images_to_pdf(image_paths, pdf_path)

                    print("☁️ Uploading to Google Drive...")
                    #upload_pdf_to_drive(pdf_path, drive_folder)

                    print("📤 Sending to Telegram...")
                    send_pdf_to_telegram(pdf_path, bot_token, chat_id, title, chapter)

                    success = True
                    print(f"✅ Successfully processed Chapter {chapter}")
                    break

                except Exception as e:
                    print(f"❌ Error: {e}")
                    traceback.print_exc()
                    if attempt == RETRY_LIMIT and alert_token and alert_chat_id:
                        print("📡 Sending failure alert...")
                        send_failure_alert(alert_token, alert_chat_id, title, chapter, str(e))

                time.sleep(3)

            print("🧹 Cleaning up temporary files...")
            try:
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")

            if not success:
                print(f"⚠️ Skipping Chapter {chapter} due to persistent failure.\n")
                break

            progress[title] = chapter + 1
            save_json(PROGRESS_PATH, progress)
            chapter += 1

    print("🏁 All titles processed.")

if __name__ == "__main__":
    main()
