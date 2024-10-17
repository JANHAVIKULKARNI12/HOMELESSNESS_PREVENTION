from flask import Flask, request, jsonify, render_template
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Set OpenAI API key from environment variables

openai.api_key = 'YOUR_OPENAI_API_KEY'
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=150
    )
    bot_response = response['choices'][0]['message']['content']
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)
