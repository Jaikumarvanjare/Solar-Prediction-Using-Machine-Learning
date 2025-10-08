document.addEventListener('DOMContentLoaded', () => {

    // --- Element Selection ---
    const form = document.getElementById('prediction_form');
    const predictButton = document.getElementById('predict_button');
    const resultContainer = document.getElementById('result_container');
    const predictionOutput = document.getElementById('prediction_output');
    const errorContainer = document.getElementById('error_container');
    const getWeatherButton = document.getElementById('get-weather-button');

    // --- Slider UI Update Logic ---
    const sliders = [
        { id: 'temperature', unit: ' °C', decimals: 1 },
        { id: 'humidity', unit: ' %', decimals: 0 },
        { id: 'wind_direction', unit: ' °', decimals: 0 },
        { id: 'wind_speed', unit: ' km/h', decimals: 1 },
        { id: 'month', unit: '', decimals: 0 },
        { id: 'hour', unit: '', decimals: 0 },
    ];

    sliders.forEach(sliderInfo => {
        const slider = document.getElementById(sliderInfo.id);
        const valueSpan = document.getElementById(`${sliderInfo.id}-value`);
        if (slider && valueSpan) {
            slider.addEventListener('input', () => {
                updateSliderValue(slider, valueSpan, sliderInfo.unit, sliderInfo.decimals);
            });
        }
    });
    
    // --- Get Current Weather ---
    getWeatherButton.addEventListener('click', async () => {
        setWeatherButtonLoading(true);
        hideMessages();

        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            const apiUrl = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m`;

            try {
                const response = await fetch(apiUrl);
                const data = await response.json();
                
                if (data && data.current) {
                    const weather = data.current;
                    // Update form with weather data
                    updateFormValue('temperature', weather.temperature_2m);
                    updateFormValue('pressure', weather.pressure_msl);
                    updateFormValue('humidity', weather.relative_humidity_2m);
                    updateFormValue('wind_speed', weather.wind_speed_10m);
                    updateFormValue('wind_direction', weather.wind_direction_10m);

                    // Update time sliders to current time
                    const now = new Date();
                    updateFormValue('month', now.getMonth() + 1); // JS months are 0-11
                    updateFormValue('hour', now.getHours());
                } else {
                    displayError('Could not retrieve current weather data.');
                }

            } catch (error) {
                console.error("Weather API Error:", error);
                displayError('Failed to fetch weather data. Check your connection.');
            } finally {
                setWeatherButtonLoading(false);
            }

        }, (error) => {
            console.error("Geolocation Error:", error);
            displayError('Geolocation is required to get current weather. Please enable it in your browser.');
            setWeatherButtonLoading(false);
        });
    });

    // --- Event Listener for Form Submission ---
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Stop the default form submission

        setLoadingState(true);
        hideMessages();

        // --- Data Collection from Form ---
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        // --- API Call to Backend ---
        try {
            // IMPORTANT: The URL for the API endpoint is now just /predict
            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (response.ok) {
                const hour = parseInt(payload.hour);
                if (hour < 6 || hour > 19) {
                    displayPrediction(0);
                } else {
                    displayPrediction(result.prediction);
                }

            } else {
                displayError(result.error || 'An unknown server error occurred.');
            }
        } catch (error) {
            displayError('Could not connect to the prediction server. Is it running?');
        } finally {
            setLoadingState(false);
        }
    });

    // --- UI Helper Functions ---
    function updateFormValue(id, value) {
        const input = document.getElementById(id);
        if (input) {
            input.value = Math.round(value * 10) / 10; // Round to 1 decimal place
            // Manually trigger the input event to update the slider's display value
            input.dispatchEvent(new Event('input'));
        }
    }
    
    function updateSliderValue(slider, valueSpan, unit, decimals) {
        const value = parseFloat(slider.value).toFixed(decimals);
        valueSpan.textContent = `${value}${unit}`;
    }

    function displayPrediction(value) {
        const formattedValue = Number.parseFloat(value).toFixed(2);
        predictionOutput.textContent = formattedValue;
        resultContainer.classList.remove('hidden');
    }

    function displayError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    }

    function hideMessages() {
        resultContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
    }

    function setLoadingState(isLoading) {
        predictButton.disabled = isLoading;
        predictButton.innerHTML = isLoading ? '<span>Predicting...</span>' : '<span>Predict Energy Output</span>';
    }

    function setWeatherButtonLoading(isLoading) {
        getWeatherButton.disabled = isLoading;
        getWeatherButton.textContent = isLoading ? 'Fetching...' : 'Use Current Weather';
    }
});


