import os
import requests
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from ai_engine import identify_food  # Import our AI function

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'supersecretkey123' 

# OLD (SQLite) 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pantry.db'

# NEW (PostgreSQL):
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/pantry_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload folder if missing
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False) # THIS WAS MISSING
    password = db.Column(db.String(150), nullable=False)


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
            flash('Error: Passwords do not match!')
            return redirect(url_for('register'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Error: Email already registered. Please login.')
            return redirect(url_for('login'))

        new_user = User(username=username, email=email, password=password) 
        
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
        
        print(f"DEBUG: Trying to login with Email: {email}")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"DEBUG: User Found! stored_password: '{user.password}' vs input_password: '{password}'")
            if user.password == password:
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                print("DEBUG: Password mismatch.")
                flash('Incorrect password.', 'danger')
        else:
            print("DEBUG: User not found in database.")
            flash('Email not found. Please Register first.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    items = PantryItem.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', items=items)

@app.route('/delete/<int:id>')
@login_required
def delete_item(id):
    item = PantryItem.query.get(id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed.')
    return redirect(url_for('dashboard'))

@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    if request.method == 'POST':
        print("DEBUG: Scan request received!") 
        
        # 1. Check if image is present
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
                print(f"DEBUG: File saved to {filepath}") 

                print("DEBUG: Calling AI model...") 
                
                label, confidence = identify_food(filepath) 
                
                print(f"DEBUG: AI predicted: {label} with confidence {confidence}") 

                new_item = PantryItem(name=label, user_id=current_user.id)
                db.session.add(new_item)
                db.session.commit()
                print("DEBUG: Item saved to database!") 
                
                flash(f'Found {label}! Added to pantry.', 'success')
                return redirect(url_for('dashboard'))

            except Exception as e:
                print(f"ERROR: {e}") 
                flash(f'Error processing image: {str(e)}', 'danger')
                return redirect(request.url)

    return render_template('scan.html')

@app.route('/get_recipes', methods=['GET', 'POST'])
@login_required
def get_recipes():
    # 1. Get User Preference (Veg vs Non-Veg)
    # Default is 'all' (Non-Veg/No Restriction)
    diet_filter = request.args.get('diet', 'all') 
    
    # 2. Get Ingredients
    if request.method == 'POST':
        selected = request.form.getlist('selected_ingredients')
    else:
        # If just switching Veg/Non-Veg, keep previous ingredients if possible
        # For now, we default to "All Pantry Items" to keep it simple
        items = PantryItem.query.filter_by(user_id=current_user.id).all()
        selected = [item.name for item in items]

    if not selected:
        flash("Your pantry is empty! Scan some items first.", "warning")
        return redirect(url_for('dashboard'))

    ingredient_string = ",".join(selected)
    
    # 3. Spoonacular API Setup
    API_KEY = "70d76ed0153049a6be5e0e8f2b92b7f8"  
    
    url = "https://api.spoonacular.com/recipes/complexSearch"
    
    params = {
        'apiKey': API_KEY,
        'includeIngredients': ingredient_string,
        'number': 12,
        'sort': 'min-missing-ingredients', 
        'fillIngredients': True,
        'addRecipeInformation': True, 
        'ignorePantry': True
    }

    # 4. APPLY THE VEG FILTER
    if diet_filter == 'veg':
        params['diet'] = 'vegetarian'
        print("DEBUG: Searching for VEG recipes only.")
    else:
        print("DEBUG: Searching for ALL (Non-Veg) recipes.")

    try:
        response = requests.get(url, params=params)
        data = response.json()
        recipes = data.get('results', [])
    except Exception as e:
        print(f"Error: {e}")
        recipes = []

    # Pass the current 'diet_filter' back to HTML so we know which button to highlight
    return render_template('recipes.html', recipes=recipes, current_diet=diet_filter)

# --- 2. EDIT ITEM ROUTE (For the Pencil Icon) ---
@app.route('/edit_item/<int:id>', methods=['POST'])
@login_required
def edit_item(id):
    item = PantryItem.query.get_or_404(id)
    
    # Security Check: Ensure user owns this item
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