import requests

def send_telegram_alert(message):
    bot_token = "Enter your bot id"
    chat_id = "enter your chatid"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.get(url, params=payload)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", e)

# Test Message
send_telegram_alert("Test message from EV monitoring system.")

