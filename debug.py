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

output = ""

# Buscar la definición de initPrice16688 y capturar sus primeros 3000 chars
match = re.search(r'function initPrice16688\(\).{0,5000}', html, re.DOTALL)
if match:
    output += "=== initPrice16688 ===\n" + match.group(0)[:4000] + "\n\n"

# Buscar también getFilteredOptions(216) — el 216 parece ser el atributo de peso
match2 = re.search(r'getFilteredOptions.{0,3000}', html, re.DOTALL)
if match2:
    output += "=== getFilteredOptions ===\n" + match2.group(0)[:4000] + "\n\n"

if not output:
    output = "No se encontraron las funciones. Buscando '16688' en el HTML:\n"
    matches = [m.start() for m in re.finditer('16688', html)]
    for pos in matches[:5]:
        output += f"\n--- Posición {pos} ---\n{html[max(0,pos-100):pos+500]}\n"

send_telegram(output)
