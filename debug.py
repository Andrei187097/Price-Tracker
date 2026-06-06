import requests
import re
import os

URL = 'https://www.hsnstore.com/marcas/sport-series/evowhey-protein'
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    for i in range(0, len(message), 4000):
        requests.post(url, json={'chat_id': CHAT_ID, 'text': message[i:i+4000]})

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9',
}
response = requests.get(URL, headers=headers, timeout=10)
html = response.text

# Sacar 500 caracteres alrededor de "16767" para ver la estructura exacta
for pid in ['16767', '23792']:
    pos = html.find(f'"{pid}"')
    if pos != -1:
        send_telegram(f"=== Contexto raw de {pid} ===\n" + html[pos:pos+500])
    else:
        send_telegram(f"No se encontró {pid} en el HTML")
