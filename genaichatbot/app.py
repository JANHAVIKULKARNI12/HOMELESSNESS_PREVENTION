from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)

# Set the OpenAI API key directly (replace with your actual key for testing)
openai.api_key = " "

# Helper function to communicate with OpenAI
def generate_response(user_message):
    try:
        # Send user input to OpenAI's GPT model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in homelessness prevention."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error occurred during API call: {e}")
        return "Sorry, I encountered an issue processing your request. Please try again."

@app.route('/')
def home():
    return render_template('chatbot_genai.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get("message", "")
    response = generate_response(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)



