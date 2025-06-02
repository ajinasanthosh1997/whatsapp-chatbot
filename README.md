# WhatsApp ChatGPT Integration using Django

This project connects OpenAI's ChatGPT with WhatsApp using Django and the WhatsApp Cloud API. It includes setup using a virtual environment, local development server, and ngrok for webhook testing.

---

## 🚀 Setup Instructions

### 1. Clone the Repository

* https://github.com/ajinasanthosh1997/whatsapp-cahtbot.git

* cd whatsapp-cahtbot

### 2. Create and Activate Virtual Environment

#### For macOS/Linux:
* python3 -m venv venv
* source venv/bin/activate

#### For Windows:
* python -m venv venv
* venv\Scripts\activate

### 3. Install Required Dependencies

* pip install -r req.txt

### 4. Create Environment File
Create a .env file in your project root and add the following variables:

OPENAI_API_KEY=your_openai_key

OPENAI_MODEL=gpt-3.5-turbo

WHATSAPP_TOKEN=your_whatsapp_token

WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

WHATSAPP_APP_SECRET=your_app_secret

VERIFY_TOKEN=your_custom_verify_token

### 5. Run Migrations and Start Server

* python manage.py migrate
* python manage.py runserver

The server will run at:
👉 http://127.0.0.1:8000/

### 6. Expose Local Server using Ngrok
Install ngrok and expose the Django server:

* ngrok http 8000

You will receive a URL like:

Forwarding https://abcd1234.ngrok.io -> http://127.0.0.1:8000

Use this ngrok HTTPS URL when setting up the webhook in the Meta Developer Portal.

### 🌐 WhatsApp Webhook Setup
Configure your webhook with:

Callback URL:
https://abcd1234.ngrok.io/webhook/

Verify Token:
The same value as VERIFY_TOKEN from .env

### 💡 Tips
Use python manage.py createsuperuser to access the Django admin panel.

Ngrok URLs change unless you have a paid plan. Update the webhook when restarting ngrok.

Don't commit .env to version control (add it to .gitignore).

## 📌 Common Commands

#### Activate virtual environment
* source venv/bin/activate   # macOS/Linux
* venv\Scripts\activate      # Windows

#### Run development server
python manage.py runserver

#### Expose server via ngrok
ngrok http 8000
📦 Example Requirements
Make sure your requirements.txt includes:

* Django>=4.2
* openai>=1.0
* python-dotenv
* requests
