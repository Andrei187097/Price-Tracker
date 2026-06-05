import requests
from bs4 import BeautifulSoup
import json
import os
import re

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
soup = BeautifulSoup(response.text, 'html.parser')

output = ""

# Buscar en TODOS los scripts cualquier mención a precio o variante
keywords = ['optionPrice', 'jsonConfig', 'jsonSwatch', 'finalPrice', '500', 'weight', 'gramo', 'option']

for i, script in enumerate(soup.find_all('script')):
    content = script.string or ""
    if any(k in content for k in keywords):
        output += f"=== SCRIPT #{i} (type={script.get('type','none')}) ===\n"
        output += content[:2000] + "\n...\n"  # Primeros 2000 chars

if not output:
    output = "No se encontró nada relevante en ningún script.\n"
    output += f"Total scripts en la página: {len(soup.find_all('script'))}\n"
    output += f"Status HTTP: {response.status_code}\n"

send_telegram(output)
