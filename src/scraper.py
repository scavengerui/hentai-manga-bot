import requests
from bs4 import BeautifulSoup

def scrape_image_urls(chapter_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(chapter_url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"❌ Failed to fetch page: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    reader_div = soup.find("div", id="readerarea")
    if not reader_div:
        raise Exception("❌ No #readerarea div found")

    noscript = reader_div.find("noscript")
    if not noscript:
        raise Exception("❌ No <noscript> tag found inside readerarea")

    noscript_soup = BeautifulSoup(noscript.decode_contents(), "html.parser")
    image_tags = noscript_soup.find_all("img")

    image_urls = [img.get("src") for img in image_tags if img.get("src")]

    if not image_urls:
        raise Exception("❌ No image URLs found in noscript")

    return image_urls
