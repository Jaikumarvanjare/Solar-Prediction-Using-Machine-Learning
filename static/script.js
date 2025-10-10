// This script handles all frontend interactions for the Solar Prediction App.

// Wait until the entire HTML document is loaded and parsed before running the script.
document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Element Selection ---
    // Get references to all the HTML elements we need to interact with.
    const form = document.getElementById('prediction-form');
    const predictButton = document.getElementById('predict-button');
    const buttonText = predictButton.querySelector('.button-text');
    const buttonLoader = predictButton.querySelector('.button-loader');
    const resultContainer = document.getElementById('result-container');
    const predictionOutput = document.getElementById('prediction-output');
    const errorContainer = document.getElementById('error-container');

    // --- 2. Slider UI Configuration & Initialization ---
    // An array of objects to configure each slider and its display.
    const sliders = [
        { id: 'temperature', unit: ' °C', decimals: 1 },
        { id: 'humidity', unit: ' %', decimals: 0 },
        { id: 'wind_direction', unit: ' °', decimals: 0 },
        { id: 'wind_speed', unit: ' km/h', decimals: 1 },
        { id: 'month', unit: '', decimals: 0 },
        { id: 'hour', unit: '', decimals: 0 },
    ];

    sliders.forEach(sliderConfig => {
        const sliderElement = document.getElementById(sliderConfig.id);
        const valueElement = document.getElementById(`${sliderConfig.id}-value`);
        
        // Ensure both the slider and its value display element exist.
        if (sliderElement && valueElement) {
            // Add an 'input' event listener to update the text in real-time as the slider moves.
            sliderElement.addEventListener('input', () => {
                const value = parseFloat(sliderElement.value).toFixed(sliderConfig.decimals);
                valueElement.textContent = `${value}${sliderConfig.unit}`;
            });
        }
    });

    // --- 3. Main Event Listener for Form Submission ---
    form.addEventListener('submit', async (event) => {
        // Prevent the browser's default behavior of reloading the page on form submission.
        event.preventDefault(); 
        
        setLoadingState(true);
        hideMessages();

        // Create a data object from the form fields.
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        // --- 4. API Call to Backend ---
        try {
            // Use the Fetch API to send data to our '/predict' endpoint.
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            // Parse the JSON response from the server.
            const result = await response.json();

            if (response.ok) {
                // If the server responds with a success status code (e.g., 200).
                
                // Add a simple business logic rule: solar panels don't work at night.
                const hour = parseInt(payload.hour, 10);
                const isNight = hour < 6 || hour > 19;
                
                // If it's night, show 0. Otherwise, show the model's prediction.
                const finalPrediction = isNight ? 0 : result.prediction;
                displayPrediction(finalPrediction);

            } else {
                // If the server responds with an error status code (e.g., 400, 500).
                displayError(result.error || 'An unknown server error occurred.');
            }
        } catch (error) {
            // This block catches network errors (e.g., server is down, no internet).
            console.error("Fetch Error:", error);
            displayError('Could not connect to the server. Please try again later.');
        } finally {
            // This block runs regardless of whether the request succeeded or failed.
            // It ensures the button is re-enabled.
            setLoadingState(false);
        }
    });

    // --- 5. UI Helper Functions ---

    /** Displays the prediction result in the UI. */
    function displayPrediction(value) {
        const formattedValue = Number.parseFloat(value).toFixed(2);
        predictionOutput.textContent = formattedValue;
        resultContainer.classList.remove('hidden');
    }

    /** Displays an error message in the UI. */
    function displayError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    }

    /** Hides both the result and error message containers. */
    function hideMessages() {
        resultContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
    }

    /** Toggles the button's state between loading and active. */
    function setLoadingState(isLoading) {
        predictButton.disabled = isLoading;
        buttonText.classList.toggle('hidden', isLoading);
        buttonLoader.classList.toggle('hidden', !isLoading);
    }
});

