# WhatsApp ChatGPT Integration using Django

This project integrates OpenAI's ChatGPT with WhatsApp using Django and the WhatsApp Cloud API. It includes steps to configure Meta Developer credentials, run a local server with Django, and expose it using ngrok for webhook testing.

---

## 🚀 Project Setup

### 1. Clone the Repository

* git clone https://github.com/your-username/whatsapp-chatgpt-django.git
* cd whatsapp-chatgpt-django
  
### 2. Create and Activate Virtual Environment

#### macOS/Linux:
* python3 -m venv venv
* source venv/bin/activate

#### Windows:

* python -m venv venv
* venv\Scripts\activate
  
### 3. Install Dependencies
  
* pip install -r requirements.txt
  
### 4. Create .env File

OPENAI_API_KEY=your_openai_key

OPENAI_MODEL=gpt-3.5-turbo

WHATSAPP_TOKEN=your_whatsapp_access_token

WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

WHATSAPP_APP_SECRET=your_app_secret

VERIFY_TOKEN=your_custom_verify_token

⚠️ Never commit your .env file to version control.

### 5. Meta (Facebook Developer) Setup Guide
   
#### 🔧 Create Your App and Get WhatsApp API Credentials

* Go to https://developers.facebook.com

* Click "My Apps" > "Create App"

* Choose "Business" as the app type.

* Fill out app details and click "Create App".

* In your app dashboard, add "WhatsApp" as a product.

* Under WhatsApp > Getting Started, you’ll find:

* WHATSAPP_TOKEN → Temporary access token (use this for development).

* WHATSAPP_PHONE_NUMBER_ID → Phone number ID.

* Business Account ID (not needed for .env but visible here).

* Click "Add Phone Number" to link your test number.

* Save the credentials and use them in your .env.

#### 6. Set Up Webhook

* Go to WhatsApp > Configuration > Webhooks in the Meta Developer portal.

* Set the Callback URL to your ngrok HTTPS URL (see below) + /webhook/, for example:

* https://abcd1234.ngrok.io/webhook/
Set the Verify Token to the same value as VERIFY_TOKEN in your .env.

Subscribe to messages event.

### 7. Run Django Server

* python manage.py migrate
* python manage.py runserver
  
### 8. Expose Server with Ngrok

Install ngrok from https://ngrok.com and run:

* ngrok http 8000
  
Use the HTTPS URL provided by ngrok as your webhook base URL.

### 🧪 Testing WhatsApp

Send a message from your test WhatsApp number to the test phone number from Meta.

OpenAI's response will be returned via your webhook and sent back to WhatsApp.

All messages and responses are stored in your database (Conversation, Message models).

### ✅ Sample .env

OPENAI_API_KEY=sk-...

OPENAI_MODEL=gpt-3.5-turbo

WHATSAPP_TOKEN=EAA...

WHATSAPP_PHONE_NUMBER_ID=123456789012345

WHATSAPP_APP_SECRET=abc123...

VERIFY_TOKEN=my_custom_token

### 🧾 Example Requirements

Django>=4.2
openai>=1.0
python-dotenv
requests

### 📌 Commands Reference

#### Activate virtual environment

* source venv/bin/activate  # macOS/Linux
* venv\Scripts\activate     # Windows

#### Run development server

* python manage.py runserver

#### Start ngrok tunnel

* ngrok http 8000
