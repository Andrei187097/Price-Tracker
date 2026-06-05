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

# Buscar el array de options del atributo 216 con sus labels
match = re.search(r'"id":"216".*?"options":\[(.{0,3000}?)\]', html, re.DOTALL)
if match:
    output += "=== Options array atributo 216 ===\n[" + match.group(1) + "]\n\n"

# Buscar labels de los IDs conocidos: 3486, 1854
for opt_id in ['3486', '1854', '6045']:
    match2 = re.search(rf'"id":"{opt_id}","label":"([^"]+)"', html)
    if match2:
        output += f"Option {opt_id} = {match2.group(1)}\n"

# Buscar optionPrices con los product IDs que nos interesan
# Los productos del 3486: primer ID es 23792
# Los productos del 1854: primer ID es 16767
for pid in ['23792', '16767', '16734', '16759']:
    match3 = re.search(rf'"{pid}".{{0,200}}finalPrice', html, re.DOTALL)
    if match3:
        output += f"\n=== Precio producto {pid} ===\n{match3.group(0)[:300]}\n"

if not output:
    output = "Nada encontrado."

send_telegram(output)
