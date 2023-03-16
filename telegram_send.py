import requests
import config_parser as cp



def send_telegram_message(message):
    config_data = cp.read_config()
    TOKEN = config_data['telegram_credentials']['token']
    CHAT_ID = config_data['telegram_credentials']['chat_id']
    message = message
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    print(requests.get(url).json())