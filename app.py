# ----------------- [Imports] -----------------
import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import logging

# ----------------- [App Initialization & Configuration] -----------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ----------------- [Model Loading] -----------------
try:
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    app.logger.info("Model loaded successfully from model.pkl.")
except FileNotFoundError:
    app.logger.error("FATAL ERROR: 'model.pkl' not found. Ensure it's in the same folder as app.py.")
    model = None
except Exception as e:
    app.logger.error(f"FATAL ERROR: An unexpected error occurred while loading the model: {e}")
    model = None

# ----------------- [Routes] -----------------
@app.route('/')
def home():
    """ Serves the main HTML page. """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """ Handles the prediction logic based on the correct 7 model features. """
    app.logger.info("Received a request on the /predict endpoint.")
    if model is None:
        app.logger.error("Prediction failed because the model is not loaded.")
        return jsonify({'error': 'The machine learning model is not available. Please check server logs.'}), 500
    
    try:
        data = request.get_json(force=True)
        app.logger.info(f"Data received from frontend: {data}")

        # --- FIX: Create the feature list with the 7 correct features the model expects. ---
        feature_list = [
            float(data['temperature']),
            float(data['pressure']),
            float(data['humidity']),
            float(data['wind_direction']),
            float(data['wind_speed']),
            int(data['month']),
            int(data['hour'])
        ]
        app.logger.info(f"Features prepared for model (7 total): {feature_list}")

        features_for_prediction = np.array(feature_list).reshape(1, -1)
        prediction_result = model.predict(features_for_prediction)
        
        # Handle different model output types (Keras vs. Scikit-learn)
        # Keras often returns a nested array, Scikit-learn returns a flat array.
        if isinstance(prediction_result[0], (list, np.ndarray)):
            output = round(float(prediction_result[0][0]), 2)
        else:
            output = round(float(prediction_result[0]), 2)

        app.logger.info(f"Prediction successful. Result: {output}")
        return jsonify({'prediction': output})

    except KeyError as e:
        app.logger.error(f"Prediction Error: A required field was missing - {e}")
        return jsonify({'error': f'Missing input data for: {e}.'}), 400
    except Exception as e:
        app.logger.error(f"Prediction Error: An unexpected error occurred - {e}")
        return jsonify({'error': 'An internal server error occurred during prediction.'}), 500

# ----------------- [App Execution] -----------------
if __name__ == "__main__":
    app.run(debug=True)

