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
```
**2. Set up a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Database Configuration**
Ensure PostgreSQL is installed and running on your local machine. Create a database named pantry_db. Update the SQLALCHEMY_DATABASE_URI in app.py if your Postgres credentials differ:
```Python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/pantry_db'
```

**5. Add your AI Model**
Ensure your compiled Keras model *(food_model.keras)* is placed in the root directory next to *app.py*.

**6. Run the Application**
```bash
python app.py
```
The application will be available at **http://127.0.0.1:5000**.

## Future Scope
* Dataset Expansion: Scale the training dataset to 500+ images per class to improve real-world validation accuracy and generalization.
* Fine-Tuning: Unfreeze the top layers of the MobileNetV2 base to allow for deeper feature extraction specific to grocery items.
* Multi-Item Detection: Transition from single-image classification to object detection (e.g., YOLO) to scan multiple pantry items in a single photo.
