from google import genai
import json
import os
from PIL import Image

def extract_product_data(images):
    # Preprocess images to standardize format and reduce payload size
    processed_images = []
    for img in images:
        if img.mode != "RGB":
            img = img.convert("RGB")
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        processed_images.append(img)
    images = processed_images

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY found. Returning mock data.")
        return {
            "ITEM_NAME": "MOCK BRAND 500G TUB SPREAD",
            "BARCODE": "1234567890123",
            "MANUFACTURER": "MOCK INC.",
            "BRAND": "MOCK BRAND",
            "WEIGHT": "500G",
            "PACKAGING  TYPE": "TUB",
            "COUNTRY": "MOCKLAND",
            "VARIANT": "ORIGINAL",
            "TYPE": "SPREAD",
            "FRAGRANCE_FLAVOR": "",
            "PROMOTION": "",
            "ADDONS": "",
            "TAGLINE": "BEST MOCK EVER"
        }
        
    prompt = """
    You are an expert data entry assistant for an Item Master Database (IMDB).
    I am providing you with multiple images of the SAME product from different angles.
    Aggregate all information found across all images to produce a single complete record.
    
    Extract the following fields EXACTLY. For every field, return an object containing "value" (the extracted string) and "confidence" (a number from 0.0 to 1.0 indicating how certain you are).
    
    CRITICAL INSTRUCTION FOR ITEM_NAME: 
    You MUST construct the ITEM_NAME dynamically by concatenating the following extracted fields in this EXACT order, separated by a single space. Include a field only if it is applicable/found:
    BRAND + [Variant / Flavor / Marketing Description] + WEIGHT + PACKAGING TYPE + [PRODUCT TYPE] + [MANUFACTURER or COMPANY] + [COUNTRY]
    Ensure you correct any spelling mistakes from the package and do not include any typos. Do not transcribe from the image tag at the bottom.
    
    Fields to extract:
    - ITEM_NAME: Construct this string according to the formula: BRAND + [Variant/Flavor/Tagline] + WEIGHT + PACKAGING TYPE + [TYPE] + [MANUFACTURER] + [COUNTRY]
    - BARCODE: Numeric string only, no spaces
    - MANUFACTURER: Company name
    - BRAND: Brand name
    - WEIGHT: Net weight/volume
    - PACKAGING  TYPE: Look at the item and determine the packaging type. Use one of these samples or similar: POUCH, BOX, PLASTIC BOTTLE, SACHET, TIN, TUB, GLASS JAR.
    - COUNTRY: Country of origin
    - VARIANT: E.g., ORIGINAL, LOW FAT (leave empty if none)
    - TYPE: Product type e.g., MARGARINE, MAYONNAISE
    - FRAGRANCE_FLAVOR: Flavor/fragrance (leave empty if none)
    - PROMOTION: E.g., 50% OFF (leave empty if none)
    - ADDONS: E.g., SPOON INCLUDED (leave empty if none)
    - TAGLINE: Short promotional phrase (leave empty if none)
    
    If a field is missing, set "value" to an empty string and "confidence" to 1.0. DO NOT GUESS.
    
    Example format:
    {
      "ITEM_NAME": {"value": "BLUE BAND 250G", "confidence": 0.99},
      "VARIANT": {"value": "", "confidence": 1.0}
    }
    
    Return ONLY a raw valid JSON object. Do not include markdown formatting.
    """
    
    try:
        client = genai.Client(api_key=api_key)
        
        models_to_try = [
            'gemini-2.5-flash', 
            'gemini-2.0-flash', 
            'gemini-1.5-flash-latest', 
            'gemini-1.5-pro', 
            'gemini-pro-vision'
        ]
        
        response = None
        last_error = None
        
        for m in models_to_try:
            try:
                print(f"Trying model: {m}...")
                response = client.models.generate_content(
                    model=m,
                    contents=[prompt] + images
                )
                print(f"Successfully used {m}!")
                break
            except Exception as e:
                print(f"Model {m} failed: {e}")
                last_error = e
                continue
                
        if not response:
            raise Exception(f"All model fallbacks failed. Last error: {last_error}")
                
        text = response.text.strip()
        print(f"Raw model response: {text}")
        
        import re
        # Find the first JSON object in the text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("No JSON object found in the response.")
            
    except Exception as e:
        print(f"Extraction error: {e}")
        raise e
