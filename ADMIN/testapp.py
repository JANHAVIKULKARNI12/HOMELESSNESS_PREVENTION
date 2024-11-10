from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# Configure SQLAlchemy to use an in-memory SQLite database for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Load the model (assuming a model file is available)
try:
    model = joblib.load('homeless_model.pkl')
except FileNotFoundError:
    model = None  # Set to None if the model file is missing

# Database models
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    income_level = db.Column(db.Float)
    homeless_status = db.Column(db.Boolean, default=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'superadmin' or 'admin'

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if user.is_verified:
                session['user'] = email
                return redirect(url_for('prediction'))
            else:
                flash('Please verify your email before logging in.')
                return redirect(url_for('verify'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.')
            return redirect(url_for('login'))
        
        user = User(email=email, password=password, is_verified=False)
        db.session.add(user)
        db.session.commit()
        
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['email'] = email
        flash(f'OTP sent to {email}. Please verify your account.')
        return redirect(url_for('verify'))
    
    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        email = session.get('email')
        otp = session.get('otp')
        
        if otp and int(entered_otp) == otp:
            user = User.query.filter_by(email=email).first()
            user.is_verified = True
            db.session.commit()
            flash('Email verified successfully! You can now log in.')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('verify'))
    
    return render_template('verify.html')

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if 'user' not in session:
        flash('You must be logged in to access this page.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = [int(request.form.get(key, 0)) for key in [
            'age', 'gender', 'income_level', 'employment_status', 
            'education_level', 'mental_health_status', 'substance_abuse',
            'family_status', 'housing_history', 'disability', 'region', 'social_support'
        ]]
        prediction = model.predict([data]) if model else [0]
        result = 'Homeless' if prediction[0] == 1 else 'Not Homeless'
        return render_template('prediction.html', result=result)
    
    return render_template('prediction.html', result=None)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_role'] = admin.role
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('admin_login'))
    
    admin_role = session.get('admin_role')
    people = Person.query.all()
    admins = Admin.query.all() if admin_role == 'superadmin' else None
    return render_template('admin_dashboard.html', people=people, admins=admins, is_superadmin=(admin_role == 'superadmin'))

@app.route('/admin/add', methods=['POST'])
def add_admin():
    if 'admin_id' not in session or session.get('admin_role') != 'superadmin':
        return "Unauthorized", 403
    
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    role = request.form['role']
    
    existing_admin = Admin.query.filter_by(username=username).first()
    if existing_admin:
        flash('Username already exists')
        return redirect(url_for('admin_dashboard'))
    
    new_admin = Admin(username=username, password=password, role=role)
    db.session.add(new_admin)
    db.session.commit()
    flash('New admin added successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/authorize/<int:person_id>', methods=['POST'])
def authorize_homeless(person_id):
    if 'admin_id' not in session or session.get('admin_role') != 'superadmin':
        return "Unauthorized", 403
    
    person = Person.query.get(person_id)
    if person:
        person.homeless_status = True
        db.session.commit()
        flash(f"Homeless status authorized for person with ID: {person_id}")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_role', None)
    flash("Admin logged out successfully.")
    return redirect(url_for('admin_login'))

# Initialize database and create superadmin if it doesn't exist
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(role='superadmin').first():
        superadmin = Admin(
            username='superadmin',
            password=generate_password_hash('superpassword'),  # Replace with a secure password
            role='superadmin'
        )
        db.session.add(superadmin)
        db.session.commit()
        print("Superadmin created successfully.")

if __name__ == '__main__':
    app.run(debug=True)
