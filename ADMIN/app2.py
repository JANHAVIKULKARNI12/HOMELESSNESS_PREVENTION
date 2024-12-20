from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random
import joblib
import os

app = Flask(__name__)
app.secret_key = 'd2b1e5a836ef4259b707587f5a2b1ff23f38e7bb34b25e7b67c5a758e345e3b5'  # Replace with a secure key
socketio = SocketIO(app)

# Configure MySQL Database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Legend%40123@localhost/homeless'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: To suppress a warning

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'homelessprevention5@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'stir tdab vfmv clvr'  # Replace with your app password

db = SQLAlchemy(app)
mail = Mail(app)

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
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    booked_by = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)  # Link to Person table

    donor = db.relationship('Donor', backref=db.backref('houses', lazy=True))


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

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

        # Send OTP via email
        try:
            msg = Message('OTP Verification', sender='homelessprevention5@gmail.com', recipients=[email])
            msg.body = f'Your OTP is {otp}. Please enter it to verify your account.'
            mail.send(msg)
            flash(f'OTP sent to {email}. Please verify your account.')
        except Exception as e:
            flash('Failed to send OTP. Please check your email settings.')
            print(e)

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
        # Collect form data
        name = request.form.get('name')
        age = int(request.form.get('age', 0))
        gender = request.form.get('gender')
        income_level = float(request.form.get('income_level', 0))
        employment_status = int(request.form.get('employment_status', 0))
        education_level = int(request.form.get('education_level', 0))
        mental_health_status = int(request.form.get('mental_health_status', 0))
        substance_abuse = int(request.form.get('substance_abuse', 0))
        family_status = int(request.form.get('family_status', 0))
        housing_history = int(request.form.get('housing_history', 0))
        disability = int(request.form.get('disability', 0))
        region = int(request.form.get('region', 0))
        social_support = int(request.form.get('social_support', 0))

        # Prepare data for the model
        data = [
            age, gender, income_level, employment_status, education_level,
            mental_health_status, substance_abuse, family_status, housing_history,
            disability, region, social_support
        ]

        # Run the prediction (use [0] if the model is None)
        prediction = model.predict([data]) if model else [0]
        homeless_status = prediction[0] == 1  # True if predicted as homeless

        # Check if the person already exists in the database
        person = Person.query.filter_by(name=name, age=age).first()
        if person:
            # Update existing person’s homeless status
            person.homeless_status = homeless_status
        else:
            # Add a new person entry to the database
            person = Person(
                name=name, age=age, gender=gender, income_level=income_level,
                homeless_status=homeless_status
            )
            db.session.add(person)

        db.session.commit()  # Commit changes to the database

        # Fetch available houses if the user is predicted as homeless
        if homeless_status:
            available_houses = House.query.filter_by(availability=True).all()
            result = 'Homeless'
            return render_template('prediction.html', result=result, houses=available_houses)

        result = 'Not Homeless'
        return render_template('prediction.html', result=result, houses=None)

    return render_template('prediction.html', result=None, houses=None)


@app.route('/book_house/<int:house_id>', methods=['POST'])
def book_house(house_id):
    if 'user' not in session:
        flash('You must be logged in to book a house.')
        return redirect(url_for('login'))

    # Fetch the house by ID
    house = House.query.get(house_id)
    if house and house.availability:
        # Get the logged-in user's email from the session
        user_email = session['user']

        # Find the corresponding Person in the database
        person = Person.query.filter_by(name=user_email).first()

        if person:
            # Assign the house to the person and mark it as booked
            house.availability = False
            house.booked_by = person.id
            db.session.commit()

            # Flash success message
            flash(f'The house at {house.address}, {house.city} has been successfully booked!')
        else:
            # Handle the case where the Person is not found
            flash('Error: Your details were not found in the system. Please contact support.')
            return redirect(url_for('prediction'))
    else:
        # If the house is not available
        flash('This house is no longer available.')
    return redirect(url_for('prediction'))


# Donor Routes
@app.route('/donor/register', methods=['GET', 'POST'])
def donor_register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        donor = Donor(email=email, password=password, is_verified=True)
        db.session.add(donor)
        db.session.commit()
        flash('Donor registered successfully!')
        return redirect(url_for('donor_login'))
    return render_template('donor_register.html')

@app.route('/donor/login', methods=['GET', 'POST'])
def donor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        donor = Donor.query.filter_by(email=email).first()
        if donor and check_password_hash(donor.password, password):
            session['donor_id'] = donor.id
            return redirect(url_for('donor_dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('donor_login.html')

@app.route('/donor/dashboard', methods=['GET', 'POST'])
def donor_dashboard():
    if 'donor_id' not in session:
        return redirect(url_for('donor_login'))
    if request.method == 'POST':
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
        house = House(donor_id=session['donor_id'], address=address, city=city, state=state, zip_code=zip_code)
        db.session.add(house)
        db.session.commit()
        flash('House added!')
    houses = House.query.filter_by(donor_id=session['donor_id']).all()
    return render_template('donor_dashboard.html', houses=houses)

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
    people = Person.query.all()  # Retrieve all people records
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

@app.route('/admin/unauthorize/<int:person_id>', methods=['POST'])
def unauthorize_homeless(person_id):
    if 'admin_id' not in session or session.get('admin_role') != 'superadmin':
        return "Unauthorized", 403
    
    person = Person.query.get(person_id)
    if person:
        person.homeless_status = False
        db.session.commit()
        flash(f"Homeless status unauthorized for person with ID: {person_id}")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_role', None)
    flash("Admin logged out successfully.")
    return redirect(url_for('admin_login'))


user_inputs = {}
feature_names = [
    "age", "gender", "income_level", "employment_status", "education_level",
    "mental_health_status", "substance_abuse", "family_status", "housing_history",
    "disability", "region", "social_support"
]

@socketio.on('message')
def chatbot_message(data):
    global user_inputs
    user_input = data['message'].strip().lower()

    # Features to ask the user
    user_provided_features = ["age", "income_level", "education_level", "family_status"]

    # Handle greetings
    if user_input in ["hi", "hello"]:
        emit('response', {'message': "Hello! How can I assist you today? You can type 'predict' to start the prediction process or ask me questions!"})
        return

    # Start prediction process
    if "predict" in user_input:
        user_inputs = {}  # Reset inputs
        first_feature = user_provided_features[0]
        emit('response', {'message': f"Let's start! Please provide your {first_feature} (e.g., 30 for age)."})
        return

    # Handle input for specific features
    if len(user_inputs) < len(user_provided_features):
        current_feature = user_provided_features[len(user_inputs)]
        try:
            # Parse user input
            if user_input == "skip" or user_input == "":
                emit('response', {'message': f"{current_feature} is required. Please provide a valid value."})
            else:
                if current_feature in ["age", "income_level", "family_status"]:
                    user_inputs[current_feature] = float(user_input)
                elif current_feature == "education_level":
                    user_inputs[current_feature] = int(user_input)
                else:
                    raise ValueError("Invalid input format.")

                # Move to the next feature or finalize input collection
                if len(user_inputs) < len(user_provided_features):
                    next_feature = user_provided_features[len(user_inputs)]
                    emit('response', {'message': f"Got it. Please provide your {next_feature}."})
                else:
                    # Combine user-provided inputs with defaults
                    features = []
                    for feature in feature_names:
                        if feature in user_inputs:
                            features.append(user_inputs[feature])
                        else:
                            features.append(default_values[feature])

                    # Make prediction
                    prediction = model.predict([features])[0]
                    emit('response', {'message': f"Prediction result: {prediction}"})
        except ValueError:
            emit('response', {'message': f"Invalid input for {current_feature}. Please provide it again."})
    else:
        emit('response', {'message': "I didn't understand that. Say 'predict' to start again or greet me with 'hi' or 'hello'!"})

if __name__ == '__main__':
    # Initialize database and create superadmin if it doesn't exist
    with app.app_context():
        db.create_all()
        
        # Create superadmin if it doesn't exist
        if not Admin.query.filter_by(role='superadmin').first():
            superadmin = Admin(
                username='superadmin',
                password=generate_password_hash('superpassword'),  # Replace with a secure password
                role='superadmin'
            )
            db.session.add(superadmin)
        
        # Add sample people records for testing
        if not Person.query.first():
            sample_people = [
                Person(name="John Doe", age=35, gender="Male", income_level=15000.00, homeless_status=False),
                Person(name="Jane Smith", age=28, gender="Female", income_level=12000.00, homeless_status=False),
                Person(name="Mike Johnson", age=40, gender="Male", income_level=10000.00, homeless_status=True),
                Person(name="Emily Davis", age=30, gender="Female", income_level=20000.00, homeless_status=False),
                Person(name="Chris Lee", age=45, gender="Male", income_level=8000.00, homeless_status=True)
            ]
            db.session.bulk_save_objects(sample_people)
        
        db.session.commit()
        print("Database initialized with superadmin and sample data.")
    
    # Start the Flask application
    app.run(debug=True)
    socketio.run(app, debug=True)

