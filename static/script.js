// This script handles all frontend interactions for the Solar Prediction App.

document.addEventListener('DOMContentLoaded', () => {

    // --- Element Selection ---
    const form = document.getElementById('prediction-form');
    const predictButton = document.getElementById('predict-button');
    const buttonText = predictButton.querySelector('.button-text');
    const buttonLoader = predictButton.querySelector('.button-loader');
    const resultContainer = document.getElementById('result-container');
    const predictionOutput = document.getElementById('prediction-output');
    const errorContainer = document.getElementById('error-container');

    // --- Slider UI Configuration & Initialization ---
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
        if (sliderElement && valueElement) {
            // Add event listener to update the displayed value when the slider is moved
            sliderElement.addEventListener('input', () => {
                const value = parseFloat(sliderElement.value).toFixed(sliderConfig.decimals);
                valueElement.textContent = `${value}${sliderConfig.unit}`;
            });
        }
    });

    // --- Main Event Listener for Form Submission ---
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent the browser's default form submission
        setLoadingState(true);
        hideMessages();

        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        // --- API Call to Backend ---
        try {
            // The '/predict' endpoint is routed by vercel.json to our Python function
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (response.ok) {
                // Check if it's nighttime (e.g., before 6 AM or after 7 PM)
                const hour = parseInt(payload.hour, 10);
                const isNight = hour < 6 || hour > 19;
                
                // Override prediction to 0 if it's nighttime
                const finalPrediction = isNight ? 0 : result.prediction;
                displayPrediction(finalPrediction);
            } else {
                // Display the error message from the server
                displayError(result.error || 'An unknown server error occurred.');
            }
        } catch (error) {
            console.error("Fetch Error:", error);
            displayError('Could not connect to the prediction server. Please check your connection and try again.');
        } finally {
            setLoadingState(false);
        }
    });

    // --- UI Helper Functions ---

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

    /** Hides both the result and error containers. */
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

