import requests
import re
import json
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

# Extraer el bloque completo del atributo 216 con todas sus opciones
match = re.search(r'"216":\{.{0,5000}?\}(?=,"[0-9]+":|}\s*;)', html, re.DOTALL)
if match:
    output += "=== Atributo 216 completo ===\n" + match.group(0)[:4000] + "\n\n"

# Extraer optionPrices del initConfigurableSwatchOptions_16688
match2 = re.search(r'initConfigurableSwatchOptions_16688[^{]*\{.{0,8000}', html, re.DOTALL)
if match2:
    block = match2.group(0)
    # Buscar optionPrices dentro
    prices_match = re.search(r'optionPrices.{0,3000}', block, re.DOTALL)
    if prices_match:
        output += "=== optionPrices en initConfigurableSwatchOptions_16688 ===\n" + prices_match.group(0)[:3000]

if not output:
    output = "Nada encontrado."

send_telegram(output)
