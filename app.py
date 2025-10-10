# This is your Flask application.
# It handles the web server, loads the machine learning model,
# and provides an API endpoint for predictions.

from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import logging

# --- 1. App Initialization ---
app = Flask(__name__)

# --- 2. Logging Configuration ---
# This helps you see what's happening in the terminal when the app is running.
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# --- 3. Load Machine Learning Model ---
# We load the model once when the server starts to avoid reloading it on every request.
try:
    # Ensure 'model.pkl' is in the same directory as this 'app.py' file.
    model = pickle.load(open('model.pkl', 'rb'))
    app.logger.info("✅ Machine learning model loaded successfully.")
except FileNotFoundError:
    app.logger.error("❌ FATAL: 'model.pkl' not found. The app cannot make predictions.")
    model = None
except Exception as e:
    app.logger.error(f"❌ FATAL: An unexpected error occurred while loading the model: {e}")
    model = None

# --- 4. Application Routes ---

@app.route('/')
def home():
    """
    Serves the main HTML page when a user visits the root URL.
    Flask automatically looks for this file in a 'templates' folder.
    """
    app.logger.info("Serving the main page: index.html")
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    This is the core API endpoint. It receives data from the frontend,
    runs a prediction, and returns the result as JSON.
    """
    app.logger.info("Received a request on the /predict endpoint.")

    # First, check if the model was loaded correctly on startup.
    if model is None:
        error_msg = "The machine learning model is not available. Check server logs for errors."
        return jsonify({'error': error_msg}), 500

    try:
        # Get the JSON data sent from the frontend's fetch request.
        data = request.get_json()
        app.logger.info(f"Received data: {data}")

        # IMPORTANT: The order of features here MUST EXACTLY match the
        # order your model was trained on.
        features = [
            float(data['temperature']),
            float(data['pressure']),
            float(data['humidity']),
            float(data['wind_direction']),
            float(data['wind_speed']),
            int(data['month']),
            int(data['hour'])
        ]

        # Use numpy to convert the list to the 2D array shape the model expects.
        final_features = np.array(features).reshape(1, -1)

        # Make the prediction.
        prediction_result = model.predict(final_features)

        # Format the result and send it back to the frontend.
        # Keras models often return a nested array, so we access with [0][0].
        output = round(float(prediction_result[0][0]), 2)
        app.logger.info(f"Prediction successful. Result: {output}")
        return jsonify({'prediction': output})

    except KeyError as e:
        error_msg = f"Missing data for prediction: {e}. Check if all form fields are being sent."
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 400
    except Exception as e:
        # Catch any other errors during the process.
        app.logger.error(f"An error occurred during prediction: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

# --- 5. Run the App ---
# This block allows you to run the app directly using 'python app.py'
if __name__ == '__main__':
    # debug=True will auto-reload the server when you save changes and provides better error pages.
    app.run(debug=True)

