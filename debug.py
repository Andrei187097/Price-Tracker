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

# Buscar donde se definen las opciones con sus precios por variante
patterns = [
    r'optionPrices.{0,2000}',
    r'pricesByProduct.{0,2000}',
    r'allowedProducts.{0,2000}',
    r'spConfig.{0,2000}',
    r'"216".{0,1000}',
    r'attribute_id.*?216.{0,500}',
]

for pat in patterns:
    match = re.search(pat, html, re.DOTALL)
    if match:
        output += f"=== Pattern: {pat[:30]} ===\n{match.group(0)[:2000]}\n\n"

# Buscar también la función que inicializa las opciones del producto
match = re.search(r'function initConfigurableOptions16688.{0,3000}', html, re.DOTALL)
if match:
    output += "=== initConfigurableOptions16688 ===\n" + match.group(0)[:3000]

# Buscar cualquier función init relacionada con 16688
matches = re.findall(r'function \w+16688\w*\(\)', html)
output += "\n=== Todas las funciones con 16688 ===\n" + "\n".join(matches)

if not output:
    output = "Nada encontrado."

send_telegram(output)
