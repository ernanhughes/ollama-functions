import ollama
import requests

# Define the Ollama server URL
OLLAMA_URL = "http://localhost:11434/api/generate"

# Define the Flask server URL
FUNCTION_URL = "http://localhost:9999/function"

# Function to call Ollama
def call_ollama(prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "context": {
            "functions": [
                {"name": "square", "description": "Calculates the square of a number"},
                {"name": "get_weather", "description": "Fetches the current weather for a location"}
            ]
        }
    }
    print(f"Prompt: {prompt}")
    response = requests.post(OLLAMA_URL, headers=headers, json=payload)
    print(f"Response: {response.json()}")
    return response.json()

# Function to call external functions
def call_external_function(function_name, args):
    headers = {"Content-Type": "application/json"}
    payload = {"name": function_name, "args": args}
    response = requests.post(FUNCTION_URL, headers=headers, json=payload)
    return response.json()

# Main interaction loop
if __name__ == "__main__":
    while True:
        user_input = input("Ask me anything: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Check if the user wants to call a function
        if "What is the square" in user_input:
            try:
                print(f"User input: {user_input}")
                number = int(user_input.split()[-1])
                print(f"Calling square function with argument: {number}")
                result = call_external_function("square", [number])
                print(f"Result: {result['result']}")
            except Exception as e:
                print(f"Error: {e}")
        elif "What is the weather" in user_input:
            location = user_input.split("for")[-1].strip()
            result = call_external_function("get_weather", [location])
            print(f"Temperature in {location}: {result['temperature']}°C")
        else:
            # Pass the prompt to Ollama
            response = call_ollama(user_input)
            print("Ollama Response:", response)
