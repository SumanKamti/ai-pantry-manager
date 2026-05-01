import os
import logging
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from ai_engine import identify_food  

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# PostgreSQL Database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://postgres:admin@localhost/pantry_db'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Spoonacular API Key (loaded from environment)
SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY', '')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False) 
    password = db.Column(db.String(256), nullable=False)


class PantryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Error: Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Error: Email already registered. Please login.', 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success') 
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password.', 'danger')
        else:
            flash('Email not found. Please Register first.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('_flashes', None)
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    items = PantryItem.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', items=items)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_item(id):
    item = PantryItem.query.get(id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['image']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file:
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                label, confidence = identify_food(filepath) 
                
                logger.info(f"AI predicted: {label} with confidence {confidence}%")

                # Only save items with confidence >= 60%
                if confidence < 60:
                    flash(f'AI is not confident enough. It looks like "{label}" ({confidence}% confidence). Try a clearer photo.', 'warning')
                    return redirect(url_for('scan'))

                new_item = PantryItem(name=label, user_id=current_user.id)
                db.session.add(new_item)
                db.session.commit()
                
                flash(f'Found {label} ({confidence}% confidence)! Added to pantry.', 'success')
                return redirect(url_for('dashboard'))

            except Exception as e:
                logger.error(f"Error processing image: {e}")
                flash(f'Error processing image: {str(e)}', 'danger')
                return redirect(request.url)

    return render_template('scan.html')

@app.route('/get_recipes', methods=['GET', 'POST'])
@login_required
def get_recipes():
    diet_filter = request.args.get('diet', 'all') 
    
    if request.method == 'POST':
        selected = request.form.getlist('selected_ingredients')
    else:
        items = PantryItem.query.filter_by(user_id=current_user.id).all()
        selected = [item.name for item in items]

    if not selected:
        flash("Your pantry is empty! Scan some items first.", "warning")
        return redirect(url_for('dashboard'))

    ingredient_string = ",".join(selected)
    
    # Spoonacular API Setup
    url = "https://api.spoonacular.com/recipes/complexSearch"
    
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'includeIngredients': ingredient_string,
        'number': 12,
        'sort': 'min-missing-ingredients', 
        'fillIngredients': True,
        'addRecipeInformation': True, 
        'ignorePantry': True
    }

    if diet_filter == 'veg':
        params['diet'] = 'vegetarian'

    try:
        response = requests.get(url, params=params)
        data = response.json()
        all_recipes = data.get('results', [])
        # Strict filter: only show recipes with 2 or fewer missing ingredients
        recipes = [r for r in all_recipes if r.get('missedIngredientCount', 100) <= 2]

    except Exception as e:
        logger.error(f"Spoonacular API error: {e}")
        recipes = []

    return render_template('recipes.html', recipes=recipes, current_diet=diet_filter)

# --- EDIT ITEM ROUTE---
@app.route('/edit_item/<int:id>', methods=['POST'])
@login_required
def edit_item(id):
    item = PantryItem.query.get_or_404(id)
    
    if item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
        
    new_name = request.form.get('new_name')
    
    if new_name:
        item.name = new_name 
        db.session.commit()
        flash('Item updated successfully!', 'success')
    else:
        flash('Name cannot be empty.', 'warning')
    
    return redirect(url_for('dashboard'))


# --- RUN APP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)