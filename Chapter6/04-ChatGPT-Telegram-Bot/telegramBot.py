import requests


class TelegramBot:
    def __init__(self, telegram_token):
        self.telegram_token = telegram_token
        self.base_url = 'https://api.telegram.org/bot'

    def _request(self, method, endpoint, data=None):
        if method == 'GET':
            r = requests.get(f'{self.base_url}{self.telegram_token}{endpoint}')
        else:
            r = requests.post(f'{self.base_url}{self.telegram_token}{endpoint}', json=data)
        return r.json()

    def send_message(self, data):
        return self._request('POST', '/sendMessage', data)

    def set_webhook(self, server_url):
        return self._request('POST', f'/setWebhook?url={server_url}/webhook')
