from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random
import joblib
from transformers import pipeline
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'd2b1e5a836ef4259b707587f5a2b1ff23f38e7bb34b25e7b67c5a758e345e3b5'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'homelessprevention5@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'stir tdab vfmv clvr'  # Replace with your app password

db = SQLAlchemy(app)
mail = Mail(app)

# Load homeless model
model = joblib.load('homeless_model.pkl')

# Load the Hugging Face conversational model
chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

# Route for the root URL to redirect to the login page
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('prediction'))
    return redirect(url_for('login'))

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user and user.is_verified:
            session['user'] = email
            flash('Logged in successfully!', 'success')
            return redirect(url_for('prediction'))
        elif user:
            flash('Please verify your email before logging in.', 'warning')
            return redirect(url_for('verify'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))
        
        # Save user but mark as not verified
        user = User(email=email, password=password, is_verified=False)
        db.session.add(user)
        db.session.commit()
        
        # Generate OTP and send email
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['email'] = email

        msg = Message('Verify Your Email', sender='homelessprevention5@gmail.com', recipients=[email])
        msg.body = f'Your OTP for email verification is {otp}'
        mail.send(msg)

        flash('OTP sent to your email. Please verify.', 'info')
        return redirect(url_for('verify'))
    
    return render_template('register.html')

# Route for OTP verification
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        email = session.get('email')
        otp = session.get('otp')
        if otp and int(entered_otp) == otp:
            # Mark user as verified
            user = User.query.filter_by(email=email).first()
            user.is_verified = True
            db.session.commit()
            
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            return redirect(url_for('verify'))
    
    return render_template('verify.html')

# Route for prediction (restricted to verified users)
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if 'user' not in session:
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Collect data from the form
        data = {
            'age': request.form['age'],
            'gender': request.form['gender'],
            'income_level': request.form['income_level'],
            'employment_status': request.form['employment_status'],
            'education_level': request.form['education_level'],
            'mental_health_status': request.form['mental_health_status'],
            'substance_abuse': request.form['substance_abuse'],
            'family_status': request.form['family_status'],
            'housing_history': request.form['housing_history'],
            'disability': request.form['disability'],
            'region': request.form['region'],
            'social_support': request.form['social_support'],
        }

        # Prepare data for the model
        features = [int(data[key]) for key in data]
        prediction = model.predict([features])

        if prediction[0] == 1:
            result = 'Homeless'
        else:
            result = 'Not Homeless'
        
        return render_template('prediction.html', result=result)
    
    return render_template('prediction.html', result=None)

# Route for chatbot interaction
@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    user_message = request.json.get('message')
    conversation = chatbot(user_message)
    bot_response = conversation.generated_responses[-1]  # Get the latest response
    return jsonify({"response": str(bot_response)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
