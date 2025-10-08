# This file replaces your original app.py
# It must be placed inside an 'api' folder.

import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import logging

# Vercel expects the Flask app object to be named 'app'
app = Flask(__name__, static_folder='../static', template_folder='../templates')

# --- Model Loading ---
try:
    # When deployed on Vercel, the current working directory is the root.
    model = pickle.load(open('model.pkl', 'rb'))
except FileNotFoundError:
    logging.error("model.pkl not found. Make sure it's in the root directory.")
    model = None
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None

# --- Routes ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the prediction logic."""
    if model is None:
        return jsonify({'error': 'Machine learning model is not loaded.'}), 500

    try:
        data = request.get_json()
        
        # This order MUST match the model's training order
        features = [
            float(data['temperature']),
            float(data['pressure']),
            float(data['humidity']),
            float(data['wind_direction']),
            float(data['wind_speed']),
            int(data['month']),
            int(data['hour'])
        ]

        prediction = model.predict(np.array(features).reshape(1, -1))
        
        return jsonify({'prediction': round(prediction[0], 2)})

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({'error': 'An internal error occurred during prediction.'}), 500
