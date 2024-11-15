from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Sample responses dictionary
responses = {
    "hello": "Hello! How can I assist you today?",
    "help": "I'm here to help you with information on shelters, resources, and more. Just ask your question!",
    "shelter": "Here are some nearby shelters: Shelter A, Shelter B, Shelter C.",
    "food": "You can find food resources at Food Bank X and Soup Kitchen Y.",
    "emergency": "If you're in an emergency, please call the hotline at 123-456-7890."
}

def get_response(user_input):
    # Basic keyword matching for demonstration
    for keyword, response in responses.items():
        if re.search(rf'\b{keyword}\b', user_input, re.IGNORECASE):
            return response
    return "I'm sorry, I didn't understand that. Can you try asking in a different way?"

@app.route('/')
def home():
    # Serve the chatbot HTML interface
    return render_template('chatbot.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    # Process the user's message and provide a response
    user_message = request.json.get("message", "")
    response = get_response(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
