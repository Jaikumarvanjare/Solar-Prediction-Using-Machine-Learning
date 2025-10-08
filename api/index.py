# This is your Flask application.
# It MUST be inside the 'api' folder and named 'index.py'.

from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import logging
import os

# Vercel requires the app object to be named 'app'.
# We tell Flask where to find the static and template files relative to the project root.
app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Configure logging for better debugging on Vercel
logging.basicConfig(level=logging.INFO)

# --- Load Machine Learning Model ---
model = None
try:
    # The path needs to be relative to the root of the project where Vercel runs the code.
    model_path = os.path.join(os.path.dirname(__file__), '..', 'model.pkl')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    logging.info("Model loaded successfully.")
except FileNotFoundError:
    logging.error("Error: model.pkl not found. Ensure it is in the project root directory.")
except Exception as e:
    logging.error(f"An unexpected error occurred while loading the model: {e}")

# --- Define Routes ---

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    This single route serves the main index.html file for any path.
    This ensures the single-page application loads correctly, regardless of the URL entered.
    """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    This is the API endpoint that receives data from the frontend,
    runs the prediction, and returns the result.
    """
    if not model:
        return jsonify({'error': 'The machine learning model is not available. Check server logs.'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid input: No data received.'}), 400
            
        logging.info(f"Received data for prediction: {data}")

        # The order of features here MUST EXACTLY match the order your model was trained on.
        # This order matches the user's latest feedback:
        # Temperature, UNIXTime, Humidity, Pressure, WindDirection, Speed.
        
        # We need to calculate UNIXTime from the month and hour.
        # NOTE: This is a rough approximation. A real-world app would use a full date.
        from datetime import datetime
        now = datetime.now()
        # Create a date for the 15th day of the given month and hour
        approx_date = datetime(now.year, int(data['month']), 15, int(data['hour']), 0)
        unix_time = int(approx_date.timestamp())

        features = [
            float(data['temperature']),
            unix_time,
            float(data['humidity']),
            float(data['pressure']),
            float(data['wind_direction']),
            float(data['wind_speed'])
        ]

        logging.info(f"Features prepared for model: {features}")
        
        # Reshape data for the model and make the prediction
        final_features = np.array(features).reshape(1, -1)
        prediction_result = model.predict(final_features)
        
        # Return the prediction in a JSON response, rounded to 2 decimal places
        return jsonify({'prediction': round(prediction_result[0], 2)})

    except KeyError as e:
        logging.error(f"Prediction Error: Missing key in input data - {e}")
        return jsonify({'error': f'Missing input data: {e}'}), 400
    except Exception as e:
        logging.error(f"Prediction Error: {e}")
        return jsonify({'error': 'An internal error occurred during prediction.'}), 500

