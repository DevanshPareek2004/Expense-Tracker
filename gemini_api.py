import pytesseract
import json
from PIL import Image
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_with_ocr(image_path):
    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text
    except Exception as e:
        return None

def extract_data_from_image(image_path):
    try:
        extracted_text = extract_text_with_ocr(image_path)
        
        if not extracted_text.strip():
            return {"error": "No text detected. Please upload a clearer image."}

        prompt = f"""
        Given the following extracted receipt text:
        ``` 
        {extracted_text} 
        ```
        Extract these details in **valid JSON format**:
        - "price" (total amount)
        - "date" (purchase date)
        - "category" (item category)

        **Example Response:**
        ```json
        {{
            "price": "706.00",
            "date": "09/02/25",
            "category": "Food"
        }}
        ```
        """

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([prompt])

        if response and response.text:
            try:
                extracted_data = json.loads(response.text.strip())
            except json.JSONDecodeError:
                extracted_data = manual_extraction(response.text.strip())
            
            return extracted_data

        return None

    except Exception as e:
        return None

def manual_extraction(response_text):
    extracted_data = {}
    
    price_match = re.search(r"Grand Total\s*₹\s*(\d+\.\d{2})", response_text)
    if price_match:
        extracted_data["price"] = price_match.group(1)

    date_match = re.search(r"Date:\s*(\d{2}/\d{2}/\d{2})", response_text)
    if date_match:
        extracted_data["date"] = date_match.group(1)

    extracted_data["category"] = "Food"

    return extracted_data

if __name__ == "__main__":
    image_path = "receipt.jpg"
    extracted_data = extract_data_from_image(image_path)