# This is your Flask application.
# For Render, it MUST be in the root folder and named 'app.py'.

from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import logging

# --- App Initialization ---
# When app.py is in the root, Flask automatically finds the 'static' and 'templates' folders.
app = Flask(__name__)

# --- Logging Configuration ---
# Set up basic logging to see informational messages and errors in Render's logs.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Load Machine Learning Model ---
# We wrap this in a try-except block to gracefully handle any issues on startup.
try:
    # Load the model from the root directory.
    model = pickle.load(open('model.pkl', 'rb'))
    app.logger.info("Machine learning model loaded successfully.")
except FileNotFoundError:
    app.logger.error("FATAL: model.pkl not found in the root directory. The app cannot make predictions.")
    model = None
except Exception as e:
    app.logger.error(f"FATAL: An unexpected error occurred while loading the model: {e}")
    model = None

# --- Application Routes ---

@app.route('/')
def home():
    """
    Serves the main index.html page when a user visits the root URL.
    """
    app.logger.info("Serving the main page: index.html")
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    This is the core API endpoint. It receives data from the frontend,
    runs the prediction using the loaded model, and returns the result as JSON.
    """
    app.logger.info("Received a request on the /predict endpoint.")
    
    # First, check if the model was loaded correctly on startup.
    if not model:
        return jsonify({'error': 'The machine learning model is not available. Check server logs.'}), 500

    try:
        # Get the JSON data sent from the frontend's fetch request.
        data = request.get_json()
        app.logger.info(f"Received data for prediction: {data}")

        # The order of features here MUST EXACTLY match the order your model was trained on.
        # This creates the list of numbers that the model expects.
        features = [
            float(data['temperature']),
            float(data['pressure']),
            float(data['humidity']),
            float(data['wind_direction']),
            float(data['wind_speed']),
            int(data['month']),
            int(data['hour'])
        ]
        app.logger.info(f"Features successfully prepared for model: {features}")
        
        # Use numpy to convert the list to the correct shape for scikit-learn.
        final_features = np.array(features).reshape(1, -1)
        
        # Make the actual prediction.
        prediction_result = model.predict(final_features)
        
        # Format the result and send it back to the frontend.
        output = round(prediction_result[0], 2)
        app.logger.info(f"Prediction successful. Result: {output}")
        return jsonify({'prediction': output})

    except Exception as e:
        # If any error occurs during the process, log it and return a generic error message.
        app.logger.error(f"An error occurred during prediction: {e}")
        return jsonify({'error': 'An internal error occurred during prediction.'}), 500

