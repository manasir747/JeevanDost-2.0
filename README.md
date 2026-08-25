# JeevanDost 2.0

JeevanDost 2.0 is a Flask-based Health Assistant web application. It provides an AI-powered medical chatbot, bilingual support (English/Hindi), and integrations with Supabase for user authentication and Twilio for notifications.

## Features
- **AI Chatbot**: Provides AI-based health advice by interpreting user queries using an intent-matching mechanism (`intents.json`).
- **Bilingual Interface**: Supports both English and Hindi.
- **User Authentication**: Integrated with Supabase to manage user sign-ups, logins, and data.
- **Twilio Integration**: Supports sending notifications/messages using Twilio.
- **Modern UI**: Custom HTML/CSS/JS frontend served via Flask.

## Prerequisites
- Python 3.7+
- Supabase account and project
- Twilio account (optional, for SMS features)

## Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   cd "JeevanDost 2.0"
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set the following environment variables before running the app. You can do this by exporting them in your terminal or setting them in your hosting environment (e.g., Render, Heroku).

**Supabase Configuration (Required)**
- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key.
- `SECRET_KEY`: Flask secret key for session management (default: `change_me`).

**Twilio Configuration (Optional)**
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID.
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token.
- `TWILIO_FROM_NUMBER`: Your Twilio phone number.

## Running the Application

### Development
To run the Flask application locally:
```bash
python app8.py
```
Alternatively, if `app8.py` uses standard Flask entry points:
```bash
flask --app app8.py run
```

### Production
A `Procfile` is provided for deploying with WSGI servers like Gunicorn:
```bash
gunicorn app8:app
```

## Project Structure
- `app8.py`: The main Flask application containing routing, logic, and API endpoints.
- `index_html_file.py`: Contains the main HTML structure and frontend logic for the bot.
- `intents.json`: The training dataset and response corpus for the health assistant chatbot.
- `requirements.txt`: Python dependencies.
- `Procfile`: Gunicorn configuration for production deployment.
- `config.py`: Configuration file.
- `templates/`: Directory containing Flask templates (if any are used outside `index_html_file.py`).

## Disclaimer
This is a hackathon project. The AI health advice provided by the bot is for informational purposes only and should **not** replace professional medical consultation.
