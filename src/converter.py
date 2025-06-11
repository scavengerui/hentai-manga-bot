import os
import requests
import img2pdf
import tempfile
import shutil

def download_images(image_urls, download_dir):
    os.makedirs(download_dir, exist_ok=True)
    image_paths = []

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            image_path = os.path.join(download_dir, f"page_{i+1:03}.jpg")
            with open(image_path, "wb") as f:
                f.write(response.content)
            image_paths.append(image_path)
        except Exception as e:
            print(f"❌ Failed to download image {i+1}: {e}")
            return None

    return image_paths

def convert_images_to_pdf(image_paths, output_pdf_path):
    try:
        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(image_paths))
        return output_pdf_path
    except Exception as e:
        print(f"❌ Failed to convert images to PDF: {e}")
        return None

def cleanup_temp_dir(directory):
    try:
        shutil.rmtree(directory)
    except Exception as e:
        print(f"⚠️ Could not delete temp dir: {e}")
