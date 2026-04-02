# 🍳 SnapCook

An AI-powered kitchen assistant that automates inventory tracking using Computer Vision and suggests "zero-waste" recipes based on available stock via the Spoonacular API.

## 🚀 Features

* **Smart Inventory Scanning:** Upload images of grocery items and automatically classify them using a custom-trained Deep Learning model.
* **Intelligent Recipe Generation:** Recommends "zero-waste" recipes based strictly on the items currently available in the user's digital pantry.
* **Secure User Authentication:** Encrypted login and registration system with secure session management.
* **Real-time Pantry Dashboard:** Add, edit, and delete inventory items through a responsive, modern user interface.
* **Confidence Thresholding:** The AI safely flags uncertain predictions (below 60% confidence) to ensure database accuracy.

## 💻 Tech Stack

### AI & Machine Learning
* **Framework:** TensorFlow / Keras 3
* **Model Architecture:** MobileNetV2 (Transfer Learning)
* **Techniques:** Data Augmentation, Custom Dense Head, Global Average Pooling
* **Classes:** Trained to identify 53 distinct food/grocery items.

### Backend
* **Server Framework:** Python / Flask
* **External API:** Spoonacular API (for recipe fetching)
* **Security:** Flask-Login, Werkzeug Security (pbkdf2:sha256 password hashing)

### Database
* **Database Engine:** PostgreSQL
* **ORM:** Flask-SQLAlchemy

### Frontend
* **UI/Styling:** HTML5, CSS3, Bootstrap 5.3
* **Templating:** Jinja2
* **Interactivity:** Vanilla JavaScript (for floating UI toasts and dynamic DOM updates)

## 🛠️ Installation & Setup

Follow these steps to run the project locally on your machine.

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/snapcook.git](https://github.com/yourusername/snapcook.git)
cd snapcook
