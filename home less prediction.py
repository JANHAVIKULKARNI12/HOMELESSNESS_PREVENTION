from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd

app = Flask(__name__)

# Load the trained model
model = joblib.load('homeless_model.pkl')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.get_json()
    
    # Prepare the data as it is
    data = {
        'age': [input_data['age']],
        'gender': [input_data['gender']],
        'income_level': [input_data['income_level']],
        'employment_status': [input_data['employment_status']],
        'education_level': [input_data['education_level']],
        'mental_health_status': [input_data['mental_health_status']],
        'substance_abuse': [input_data['substance_abuse']],
        'family_status': [input_data['family_status']],
        'housing_history': [input_data['housing_history']],
        'disability': [input_data['disability']],
        'region': [input_data['region']],
        'social_support': [input_data['social_support']]
    }

    # Convert the data into a DataFrame
    input_df = pd.DataFrame(data)
    
    # Make a prediction
    prediction = model.predict(input_df)
    
    # Return the result as JSON
    result = {'homeless': int(prediction[0])}
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
