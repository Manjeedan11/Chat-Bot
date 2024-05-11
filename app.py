from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
import torch
from model import NeuraNet
from nltk_utils import tokenize, stem, bag_of_words

app = Flask(__name__)
CORS(app)

# Load intents and model data
with open('intents.json', 'r') as f:
    intents = json.load(f)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
output_size = data["output_size"]
hidden_size = data["hidden_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuraNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)
model.eval()

# Function to predict tag
def predict_tag(sentence):
    X = bag_of_words(tokenize(sentence), all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    return tag

# Route for chatbot
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message']
    tags = predict_tag(message)

    for intent in intents['intents']:
        if intent['tags'] == tags:
            response = np.random.choice(intent['responses'])
            break

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
