# 🍳 SnapCook — AI-Powered Pantry Manager & Zero-Waste Recipe Generator

An intelligent kitchen assistant that automates grocery inventory tracking using **Computer Vision (MobileNetV2)** and generates personalized, zero-waste recipes via the **Spoonacular API**.

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [AI Model Details](#ai-model-details)
- [Project Structure](#project-structure)

---

## About

Household food waste is a growing global challenge. SnapCook eliminates the friction of manual pantry tracking by letting users **snap a photo** of any grocery item. The AI identifies it, logs it into a digital pantry, and suggests recipes that use only the ingredients you already own.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Image Recognition** | Upload a photo → MobileNetV2 CNN classifies the ingredient (53 categories) |
| 📊 **Smart Confidence Filter** | Only accepts predictions with ≥60% confidence to prevent database corruption |
| 🔐 **Secure Authentication** | User registration/login with PBKDF2-SHA256 password hashing |
| 📦 **Pantry Dashboard** | View, edit, and delete inventory items in a clean, responsive UI |
| 🍲 **Recipe Generator** | Queries Spoonacular API for recipes using your exact ingredients |
| 🥬 **Diet Filtering** | Toggle between Vegetarian and Non-Vegetarian recipe views |
| 🎯 **Zero-Waste Algorithm** | Strict filter shows only recipes with ≤2 missing ingredients |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, Glassmorphism UI |
| **Backend** | Python 3.10+, Flask |
| **Database** | PostgreSQL + Flask-SQLAlchemy ORM |
| **AI/ML** | TensorFlow/Keras, MobileNetV2 (Transfer Learning) |
| **Auth** | Flask-Login, Werkzeug (PBKDF2-SHA256) |
| **API** | Spoonacular REST API |

---

## 🏗 System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Browser   │────▶│  Flask App   │────▶│  PostgreSQL DB │
│  (HTML/CSS) │◀────│  (Python)    │◀────│  (Users/Items) │
└─────────────┘     └──────┬───────┘     └────────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼─────┐ ┌─────▼──────┐
              │ TensorFlow │ │ Spoonacular│
              │ MobileNetV2│ │    API     │
              │ (53 classes)│ │ (Recipes)  │
              └────────────┘ └────────────┘
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- PostgreSQL installed and running
- A Spoonacular API key ([get one free](https://spoonacular.com/food-api))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-pantry-manager.git
cd ai-pantry-manager

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the PostgreSQL database
# Open pgAdmin or psql and run:
# CREATE DATABASE pantry_db;

# 5. Configure environment variables
# Edit the .env file with your credentials:
#   SECRET_KEY=your-random-secret-key
#   DATABASE_URL=postgresql://postgres:yourpassword@localhost/pantry_db
#   SPOONACULAR_API_KEY=your-api-key

# 6. Run the application
python app.py
```

Open your browser and navigate to: `http://localhost:5000`

---

## 📱 Usage

1. **Register** an account and log in
2. **Scan** — Upload a photo of any fruit, vegetable, or pantry item
3. **Dashboard** — View your digital pantry inventory
4. **Cook** — Click "Cook Now" to get AI-curated recipes based on your stock
5. **Filter** — Toggle between Vegetarian and Non-Vegetarian recipes

---

## 🧠 AI Model Details

| Parameter | Value |
|-----------|-------|
| Base Architecture | MobileNetV2 (ImageNet pretrained) |
| Training Method | Transfer Learning (frozen base + custom head) |
| Input Size | 224 × 224 × 3 |
| Output Classes | 53 food categories |
| Training Images | ~2,480 (80/20 train/val split) |
| Data Augmentation | Rotation (20°), Zoom (0.2), Horizontal Flip |
| Final Train Accuracy | ~90.4% |
| Final Val Accuracy | ~57.6% |
| Confidence Threshold | 60% (rejects uncertain predictions) |

---

## 📂 Project Structure

```
ai-pantry-manager/
├── app.py                 # Flask application (routes, auth, API)
├── ai_engine.py           # TensorFlow model loading & prediction
├── food_model.keras       # Trained MobileNetV2 model (53 classes)
├── train.ipynb            # Jupyter notebook for model training
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore             # Git ignore rules
├── uploads/               # User-uploaded images (temporary)
└── templates/
    ├── layout.html        # Base template (navbar, footer, flash)
    ├── index.html         # Landing page (hero + features)
    ├── login.html         # Login page (glassmorphism)
    ├── register.html      # Registration page
    ├── dashboard.html     # Pantry inventory dashboard
    ├── scan.html          # Image upload & AI scan page
    └── recipes.html       # Recipe results (veg/non-veg tabs)
```

---

## 📄 License

This project was built as a Capstone Project. All rights reserved.
