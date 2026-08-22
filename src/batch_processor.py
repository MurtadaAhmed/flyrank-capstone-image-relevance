import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from PIL import Image

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class ImageMetadata(BaseModel):
    subject: str
    category: str
    attributes: list[str]
    caption: str
    confidence: float

IMAGE_DIR = "../data/images"
OUTPUT_FILE = "../data/processed_images.json"
COST_LOG_FILE = "../data/cost_log.json"

def process_image(image_path, attempt=1, max_retries=3):
    print(f"processing image {image_path}")
    prompt = """
        Analyze this image carefully. You must return a valid JSON object using exactly this schema:
        - subject (string): The main focus of the image
        - category (string): Broad classification (e.g., 'animal')
        - attributes (list of strings): Visual details
        - caption (string): A short, accurate descriptive sentence
        - confidence (float): 0.0 to 1.0 indicating how sure you are
        """
    try:
        img = Image.open(image_path)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[prompt, img],
            config=types.GenerateContentConfig(response_mime_type="application/json",)
        )
        raw_data = json.loads(response.text)
        validated = ImageMetadata(**raw_data)
        tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
        return validated.model_dump(), tokens

    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Validation error on {image_path}")
        print(e)
        return None, 0
    except Exception as e:
        if attempt < max_retries:
            print(f"API error processing {image_path}")
            print(e)
            print("Retrying in 2 seconds ...")
            time.sleep(4.5)
            return process_image(image_path, attempt + 1, max_retries)
        else:
            print(f"Failed to process image {image_path} after {max_retries} attempts")
            return None, 0

def run_batch_job():
    os.makedirs("../data", exist_ok=True)
    results = []
    cost_log = []
    total_tokens = 0

    image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Number of images found: {len(image_files)}")

    for filename in image_files:
        filepath = os.path.join(IMAGE_DIR, filename)

        data, tokens = process_image(filepath)

        if data:
            data['filename'] = filename
            results.append(data)

            cost_log.append({
                "filename": filename,
                "tokens": tokens,
                "cost_usd": 0.00
            })
            total_tokens += tokens

        time.sleep(1.5)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(COST_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "run_timestamp": time.time(),
            "total_images_processed": len(results),
            "total_tokens_used": total_tokens,
            "total_cost_usd": 0.00,
            "breakdown": cost_log
        }, f, indent=2)

    print(f"Result saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_batch_job()