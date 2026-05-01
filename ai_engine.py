import os
import logging
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Configure logging
logger = logging.getLogger(__name__)

MODEL_PATH = 'food_model.keras' 

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

# --- Initialize AI Model ---
logger.info("Initializing AI Engine...")
try:
    if os.path.exists(MODEL_PATH):
        logger.info(f"Loading AI Model from {MODEL_PATH}...")
        model = load_model(MODEL_PATH)
        logger.info("AI Model loaded successfully.")
    else:
        model = None
        logger.warning(f"Model file not found at {MODEL_PATH}")
except Exception as e:
    model = None
    logger.error(f"Error loading model: {e}")


def identify_food(image_path):
    """
    Identifies a food item from an image using the trained MobileNetV2 model.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        tuple: (predicted_label, confidence_percentage)
               Returns ("Unknown", 0.0) on error.
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return "Unknown", 0.0

    if model is None:
        logger.error("Model is not loaded. Cannot predict.")
        return "Unknown", 0.0

    try:
        # Preprocess image to match model input requirements
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0 

        # Run prediction
        predictions = model.predict(img_array)
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        predicted_label = CLASS_LABELS[predicted_class_index]
        
        logger.info(f"Prediction: '{predicted_label}' with {confidence*100:.2f}% confidence")
        
        if confidence < 0.60:
            logger.warning(f"Low confidence ({confidence*100:.2f}%). Rejecting prediction.")
            return predicted_label, round(confidence * 100, 2)

        return predicted_label, round(confidence * 100, 2)

    except Exception as e:
        logger.error(f"Model prediction failed: {e}")
        return "Unknown", 0.0