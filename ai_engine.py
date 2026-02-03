import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = "AIzaSyBCKnCaJbOT9WFzz8N3b_xVQA2ktu15npM"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

def identify_food(img_path):
    try:
        print(f"AI Engine: Analyzing {img_path} with Gemini...")
        with open(img_path, 'rb') as f:
            image_data = f.read()

        from PIL import Image
        img = Image.open(img_path)

        response = model.generate_content([
            img
        ])
        
        # Extract text
        prediction = response.text.strip()
        
        # Simple cleanup
        prediction = prediction.replace('\n', '').replace('.', '')
        
        print(f"AI Engine: Gemini identified '{prediction}'")
        
        return prediction
        
    except Exception as e:
        error_msg = str(e)
        print(f"AI Error: {error_msg}")
        
        if "429" in error_msg:
            return "Quota Exceeded (Try later)", 0.0
            
        return "Unknown", 0.0
