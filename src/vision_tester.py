import os
import json
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


def test_single_image(image_path: str):
    img = Image.open(image_path)
    prompt = """
    Analyze this image carefully. You must return a valid JSON object using exactly this schema:
    - subject (string): The main focus of the image (e.g., 'red fox', 'wolf', 'dog')
    - category (string): Broad classification (e.g., 'animal')
    - attributes (list of strings): Visual details you see in the image
    - caption (string): A short, accurate descriptive sentence
    - confidence (float): A number between 0.0 and 1.0 indicating how sure you are of the subject
    """
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[prompt, img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )
    raw_date = json.loads(response.text)
    validated_data = ImageMetadata(**raw_date)
    print(validated_data.model_dump_json(indent=2))

if __name__ == "__main__":
    test_image = "../data/images/bear (1).jpg"
    test_single_image(test_image)