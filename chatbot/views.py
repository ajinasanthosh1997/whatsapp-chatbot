import json
import logging
import os
import requests
import hmac
import hashlib
import re
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.utils import timezone
from openai import OpenAI
from .models import Conversation, Message, Order

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def verify_signature(request):
    signature = request.headers.get('X-Hub-Signature-256', '').split('sha256=')[-1]
    expected = hmac.new(
        os.getenv('WHATSAPP_APP_SECRET').encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == os.getenv('VERIFY_TOKEN'):
            return HttpResponse(challenge)
        return HttpResponse('Verification failed', status=403)

    elif request.method == 'POST':
        try:
            if not verify_signature(request):
                logger.warning("Invalid signature")
                return HttpResponse("Forbidden", status=403)

            data = json.loads(request.body)
            logger.info("Webhook payload:\n" + json.dumps(data, indent=2))

            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    for message in messages:
                        if message.get('type') == 'text':
                            user_id = message.get('from')
                            user_message = message['text']['body']
                            process_message(user_id, user_message)

            return HttpResponse('OK', status=200)

        except Exception as e:
            logger.exception("Error processing webhook")
            return HttpResponse('Error', status=500)

def process_message(user_id, text):
    conversation, _ = Conversation.objects.get_or_create(whatsapp_user_id=user_id)
    Message.objects.create(conversation=conversation, role='user', content=text)

    # ✅ Order count for today
    if "order" in text.lower() and "today" in text.lower():
        today = timezone.localtime().date()
        order_count = Order.objects.filter(created_at__date=today).count()
        response_text = (
            f"📦 You’ve placed {order_count} order{'s' if order_count != 1 else ''} today.\n"
            f"Let me know if you'd like to create a new one!"
        )
        Message.objects.create(conversation=conversation, role='assistant', content=response_text)
        send_whatsapp_message(user_id, response_text)
        return

    # ✅ Flexible order creation
    if re.search(r'\b(order|buy|get|create|i want|i need|i would like|i like)\b', text.lower()):
        try:
            # Extract all number + item pairs and single items
            item_matches = re.findall(r'(?:(\d+)?\s*([a-zA-Z]+))(?=,| and |$)', text.lower())
            item_list = []
            total_quantity = 0

            for qty, item in item_matches:
                item = item.strip()
                if not item:
                    continue
                qty = int(qty) if qty else 1
                total_quantity += qty
                item_list.append(f"{qty} {item}")

            if not item_list:
                raise ValueError("No items found.")

            formatted_items = "\n".join([f"• {item}" for item in item_list])
            order = Order.objects.create(
                customer_phone=user_id,
                quantity=total_quantity,
                items=", ".join(item_list)
            )
            response_text = (
                f"✅ Great! I've placed a new order for you.\n\n"
                f"🧾 *Order #{order.id}*:\n"
                f"{formatted_items}\n\n"
                f"Let me know if you want to add more items or need help with anything else."
            )

        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            response_text = "❌ Oops! Something went wrong while creating your order. Please try again."

        Message.objects.create(conversation=conversation, role='assistant', content=response_text)
        send_whatsapp_message(user_id, response_text)
        return

    # ✅ Fallback to OpenAI for chatting
    messages = Message.objects.filter(conversation=conversation).order_by('-timestamp')[:5]
    openai_messages = [{"role": "system", "content": "You are a friendly and helpful assistant chatting with a customer over WhatsApp. Be casual, clear, and conversational."}]
    for msg in reversed(messages):
        openai_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=openai_messages,
            max_tokens=200,
            temperature=0.8
        )
        ai_response = response.choices[0].message.content.strip()
        Message.objects.create(conversation=conversation, role='assistant', content=ai_response)
        send_whatsapp_message(user_id, ai_response)
    except Exception as e:
        logger.error(f"OpenAI Error: {str(e)}")
        send_whatsapp_message(user_id, "⚠️ Sorry, I'm having trouble responding right now. Please try again soon.")

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"WhatsApp API Error: {e}")
        if response is not None:
            logger.error(f"Status Code: {response.status_code}")
            logger.error(f"Response Body: {response.text}")
