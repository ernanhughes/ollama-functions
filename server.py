import os
import requests
import logging
import logging.config
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# -------------------------------
# Load Environment Variables from .env File
# -------------------------------
load_dotenv()

# -------------------------------
# Configuration Class
# -------------------------------
class Config:
    API_KEY = os.getenv("WEATHER_API_KEY", "your_default_api_key")
    WEATHER_API_URL = os.getenv("WEATHER_API_URL", "http://api.weatherapi.com/v1/current.json")
    LOG_FILE = os.getenv("LOG_FILE", "server.log")
    LOG_LEVEL = logging.INFO
    PORT = int(os.getenv("PORT", 9999))

# -------------------------------
# Logging Configuration
# -------------------------------
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": Config.LOG_FILE,
            "mode": "w",
            "formatter": "detailed"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed"
        }
    },
    "root": {
        "handlers": ["file", "console"],
        "level": Config.LOG_LEVEL,
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# -------------------------------
# Flask App
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Utility Functions
# -------------------------------
def square(x: int) -> int:
    """Returns the square of a number."""
    return x * x

def get_weather(location: str) -> dict:
    """Fetches the current temperature from WeatherAPI."""
    params = {"key": Config.API_KEY, "q": location}
    
    try:
        response = requests.get(Config.WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return {"temperature": data["current"]["temp_c"]}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
        return {"error": "Failed to fetch weather data"}

# -------------------------------
# Flask Routes
# -------------------------------
@app.route("/function", methods=["POST"])
def call_function():
    """Handles function calls via POST requests."""
    try:
        data = request.get_json()
        logger.info(f"Received request: {json.dumps(data)}")

        if not data or "name" not in data or "args" not in data:
            logger.warning("Invalid request format")
            return jsonify({"error": "Invalid request format"}), 400

        function_name = data["name"]
        arguments = data["args"]

        if function_name == "square":
            if not arguments or not isinstance(arguments[0], (int, float)):
                return jsonify({"error": "Invalid argument for square"}), 400
            result = square(arguments[0])
            return jsonify({"result": result})

        elif function_name == "get_weather":
            if not arguments or not isinstance(arguments[0], str):
                return jsonify({"error": "Invalid argument for get_weather"}), 400
            temperature = get_weather(arguments[0])
            return jsonify(temperature)

        else:
            logger.warning(f"Function '{function_name}' not found")
            return jsonify({"error": "Function not found"}), 404

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# -------------------------------
# Run the Application
# -------------------------------
if __name__ == "__main__":
    app.run(port=Config.PORT)
