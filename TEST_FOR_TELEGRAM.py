"""Send a manually requested Telegram connectivity test using local environment config."""
from live_prediction import load_local_env, send_telegram_alert


if __name__ == "__main__":
    load_local_env()
    if send_telegram_alert("Test message from the Substation Fault Alert System (simulation project)."):
        print("Telegram test message sent.")
    else:
        print("No test message sent; configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID first.")
