import requests
from bs4 import BeautifulSoup
import json
import os

URL = 'https://www.hsnstore.com/marcas/sport-series/evowhey-protein'
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def deep_find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            result = deep_find(v, key)
            if result is not None:
                return result
    return None

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    # Telegram tiene límite de 4096 caracteres por mensaje
    for i in range(0, len(message), 4000):
        requests.post(url, json={'chat_id': CHAT_ID, 'text': message[i:i+4000]})

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9',
}
response = requests.get(URL, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

output = ""

for script in soup.find_all('script', type='text/x-magento-init'):
    try:
        data = json.loads(script.string)
        sc = deep_find(data, 'jsonSwatchConfig')
        jc = deep_find(data, 'jsonConfig')

        if sc:
            output += "=== jsonSwatchConfig ===\n"
            output += json.dumps(sc, indent=2, ensure_ascii=False) + "\n"
        if jc:
            output += "=== optionPrices ===\n"
            output += json.dumps(jc.get('optionPrices', {}), indent=2, ensure_ascii=False) + "\n"
            output += "=== index ===\n"
            output += json.dumps(jc.get('index', {}), indent=2, ensure_ascii=False) + "\n"
    except Exception as e:
        output += f"Script ignorado: {e}\n"

if not output:
    output = "No se encontró ningún jsonSwatchConfig ni jsonConfig en la página."

send_telegram(output)
