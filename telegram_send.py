import requests


def send_telegram_message(token, chat_id, message):
    TOKEN = token
    chat_id = chat_id
    message = message
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message