import requests
import config_parser as cp
import json



def send_telegram_message(message):
    config_data = cp.read_config()
    TOKEN = config_data['telegram_credentials']['token']
    CHAT_ID = config_data['telegram_credentials']['chat_id']
    message = message
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url).json()

def send_log_file():
    config_data = cp.read_config()
    TOKEN = config_data['telegram_credentials']['token']
    CHAT_ID = config_data['telegram_credentials']['chat_id']
    document = open('_log.txt', "rb")
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    response = requests.post(url, data={'chat_id': CHAT_ID}, files={'document': document})
    # part below, just to make human readable response for such noobies as I
    #content = response.content.decode("utf8")
    #js = json.loads(content)
    #print(js)

if __name__ == '__main__':
    send_log_file()
