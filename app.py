# app.py

import logging
from flask import Flask, request, jsonify
from crew_factory import create_crew
from dotenv import load_dotenv

# --- INITIALIZATION ---

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Flask application
app = Flask(__name__)


# --- WEBHOOK ENDPOINT ---

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handles incoming POST requests from a service like ManyChat.
    It expects a JSON payload with 'user_message' and 'user_name'.
    """
    logging.info("Webhook received.")
    
    # Extract JSON data from the request
    data = request.get_json()
    if not data:
        logging.error("No JSON data received.")
        return jsonify({'error': 'Invalid JSON format'}), 400

    user_message = data.get('user_message')
    user_name = data.get('user_name', 'Freund')  # Default name if not provided

    if not user_message:
        logging.error("'user_message' not found in payload.")
        return jsonify({'error': "'user_message' is a required field"}), 400

    logging.info(f"Processing message from '{user_name}': '{user_message}'")

    try:
        # Create and run the AI crew
        instagram_crew = create_crew(user_message, user_name)
        result = instagram_crew.kickoff()
        
        logging.info(f"Crew generated response: {result}")
        
        # Return the final response in a JSON object
        # ManyChat can then parse this object to send the message.
        return jsonify({'response': result})

    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}", exc_info=True)
        # Return a generic error message to the calling service
        return jsonify({'error': 'An internal error occurred.'}), 500


# --- HEALTH CHECK ENDPOINT ---

@app.route('/health', methods=['GET'])
def health_check():
    """A simple endpoint to verify that the service is running."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # This block is for local development only.
    # For production, a proper WSGI server like Gunicorn will be used.
    app.run(host='0.0.0.0', port=8000, debug=True)