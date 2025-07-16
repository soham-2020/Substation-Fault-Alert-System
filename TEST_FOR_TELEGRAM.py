import requests

def send_telegram_alert(message):
    bot_token = "7950715421:AAE_jUOUwTpXCYXatlHAI_k-LBa1g_Xt_Po"
    chat_id = "1887823793"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.get(url, params=payload)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", e)

# Test Message
send_telegram_alert("Test message from EV monitoring system.")
