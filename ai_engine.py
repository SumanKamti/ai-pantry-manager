import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# 1. Update this to where your new model is located!
# Since you placed it in the main folder, we just use the file name.
MODEL_PATH = 'food_model.keras' 

# 2. Define your class labels (CRITICAL!)
CLASS_LABELS = [
    "Blueberry", "Gooseberry", "Tomato", "almond", "amaranth leaves",
    "apple", "apricot", "avocado", "banana", "beetroot", "brinjal", 
    "cabbage", "capsicum", "carrot", "cashew(Kaju)", "cauliflower", 
    "cherry", "cluster beans(Guvar)", "coconut", "cucumber", 
    "custard apple", "dates", "eggs", "fig", "green chili", "guava", 
    "kiwi", "lettuce", "lime", "lychee", "mango", "mint", 
    "mustard greens", "okra(bhindi)", "onion", "orange", "paneer", 
    "papaya", "peach", "peas", "pineapple", "pista", "plum", 
    "pomegranate", "potato", "radish", "spinach", "starfruit", 
    "strawberry", "sweet potato", "taro root", "walnut", "watermelon"
]

# Load the model ONCE when the app starts (This makes scanning much faster)
print("\n--- INITIALIZING AI ENGINE ---")
try:
    if os.path.exists(MODEL_PATH):
        print(f"Loading AI Model from {MODEL_PATH}... Please wait.")
        model = load_model(MODEL_PATH)
        print("✅ AI Model loaded successfully!")
    else:
        model = None
        print(f"❌ WARNING: Model file not found at {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"❌ ERROR loading model: {e}")


def identify_food(image_path):
    print(f"\n--- DEBUG: AI ENGINE SCAN STARTED ---")
    print(f"1. Reading image from: {image_path}")

    # 1. Check if the image exists
    if not os.path.exists(image_path):
        print(f"ERROR: Image file not found at {image_path}")
        return "Unknown", 0.0

    # 2. Check if the model loaded properly
    if model is None:
        print("ERROR: Model is not loaded. Cannot predict.")
        return "Unknown", 0.0

    # 3. Process and Predict
    try:
        print("2. Preprocessing image to match model requirements...")
        # CRITICAL: Change target_size to match what you used during training (e.g., 224x224 or 150x150)
        img = image.load_img(image_path, target_size=(224, 224))
        
        # Convert image to a mathematical array
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Scale pixels (Keep this if you scaled your pixels by 255 during training)
        img_array = img_array / 255.0 
        
        # ... [previous code] ...
        print("3. Feeding image to the Neural Network...")
        predictions = model.predict(img_array)
        
        # Find the highest probability score
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        
        # Map the math back to a human-readable word
        predicted_label = CLASS_LABELS[predicted_class_index]
        
        print(f"✅ SUCCESS: AI predicts '{predicted_label}' with {confidence*100:.2f}% confidence")
        
        # --- NEW: THE CONFIDENCE THRESHOLD ---
        # If the AI is less than 60% sure, don't trust it!
        if confidence < 0.60:
            print(f"⚠️ Low confidence ({confidence*100:.2f}%). Rejecting prediction.")
            return f"Not sure (Looks like {predicted_label}?)", round(confidence * 100, 2)
            
        # If it's highly confident, return normally
        return predicted_label, round(confidence * 100, 2)

    except Exception as e:
        print(f"❌ MODEL CRASHED during prediction: {e}")
        return "Unknown", 0.0