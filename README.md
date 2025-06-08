# Instagram AI Agent for Fitness Coaching

This project provides a sophisticated AI-powered chat agent designed to manage an Instagram Direct Message inbox for a fitness coach. Built with `crewAI` and powered by Google's Gemini Pro, it engages with users, answers questions, and strategically guides them towards booking a consultation.

## Architecture Overview

The system operates via a webhook-based architecture, ensuring no direct, unauthorized access to the Instagram API is required.

1.  **User Interaction (Instagram):** A user sends a DM, triggering an automation.
2.  **Webhook Trigger (ManyChat):** ManyChat captures this interaction and sends a webhook (a POST request) containing the user's message and name to our application's API endpoint.
3.  **Reverse Proxy (Nginx):** Nginx receives the public web request, provides SSL termination, and forwards it to the Gunicorn application server.
4.  **Application Server (Gunicorn):** Gunicorn manages multiple worker processes of the Flask application, ensuring stability and performance.
5.  **Web Application (Flask):** The Python Flask app receives the data, logs the request, and validates the payload.
6.  **AI Processing (`crewAI`):** The application uses the `crew_factory` to create a team of AI agents.
    * A **Router Agent** first analyzes the user's intent.
    * A **Dialog Agent**, embodying the coach's persona, crafts a context-aware response based on the router's analysis.
7.  **Response Flow:** The generated response is sent back through Flask, Gunicorn, and Nginx to ManyChat, which then delivers the message to the user on Instagram.

## Key Features

* **Persona-Driven Dialogue:** The agent's personality is based on a detailed knowledge base, ensuring all communication is authentic and on-brand.
* **Dynamic Conversation Flow:** Utilizes a router agent to analyze user intent, allowing for natural conversations instead of a rigid, scripted flow.
* **Context-Aware Memory:** The crew remembers previous parts of the conversation to provide coherent and personalized interactions.
* **Strategic Goal-Orientation:** While being helpful and conversational, the agent's underlying goal is to identify user "pain points" and guide them towards a consultation.
* **Production-Ready:** Architected with professional tools (Gunicorn, Nginx, systemd) for robust, scalable, and secure deployment.

## Project Structure

/instagram-agent
|-- app.py              # Main Flask application, handles webhooks and routing.
|-- crew_factory.py     # Creates and configures the crew, agents, and tasks.
|-- config.py           # Stores non-secret configuration variables.
|-- requirements.txt    # Python package dependencies.
|-- .env                # For storing secret API keys (must be created manually).
|-- instagram-agent.service # Example systemd service file.
|-- README.md           # This documentation file.


## Setup and Installation

### Prerequisites

* Python 3.8+
* A Google Gemini API Key
* A ManyChat Pro account
* An Instagram Business/Creator account

### Local Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/instagram-agent.git](https://github.com/your-username/instagram-agent.git)
    cd instagram-agent
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the root directory and add your API key:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```

5.  **Run the development server:**
    ```bash
    python app.py
    ```
    The application will be running on `http://127.0.0.1:8000`. For development testing, you can use a tool like `ngrok` to expose this local server to the internet for ManyChat to reach.

## API Endpoint

### `/webhook`

* **Method:** `POST`
* **Description:** The primary endpoint that receives data from ManyChat.
* **Payload (JSON):**
    ```json
    {
      "user_message": "Hello, I need some help with my training.",
      "user_name": "John"
    }
    ```
* **Success Response (200 OK):**
    ```json
    {
      "response": "Hallo John! Ich bin Christian, freut mich. Wobei genau brauchst du denn Hilfe?"
    }
    ```
* **Error Response (4xx or 5xx):**
    ```json
    {
      "error": "Descriptive error message."
    }
    ```

## Deployment

For production, the application is designed to be deployed on a Linux VPS using Gunicorn as the application server and Nginx as a reverse proxy. A detailed deployment guide is provided in the project's documentation. The process involves setting up a `systemd` service for process management and securing the endpoint with an SSL certificate via Certbot.

