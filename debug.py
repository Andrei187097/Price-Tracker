import requests
from bs4 import BeautifulSoup
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
soup = BeautifulSoup(html, 'html.parser')

output = ""

# Buscar elementos con x-data que contengan precios
for el in soup.find_all(attrs={'x-data': True}):
    xdata = el.get('x-data', '')
    if any(k in xdata for k in ['price', 'Price', 'option', 'variant', '500', 'weight']):
        output += f"=== x-data en <{el.name}> ===\n{xdata[:3000]}\n\n"

# Buscar en el HTML crudo con regex: bloques JSON que contengan precios
matches = re.findall(r'([\w]+)\s*[=:]\s*(\{[^;]{0,3000}finalPrice[^;]{0,500})', html)
for name, block in matches[:5]:
    output += f"=== Match '{name}' con finalPrice ===\n{block[:2000]}\n\n"

# Buscar también por "500" cerca de precio
matches2 = re.findall(r'.{100}500.{100}', html)
for m in matches2[:5]:
    output += f"=== Contexto '500' ===\n{m}\n\n"

if not output:
    output = "Nada encontrado. Enviando primeros 3000 chars del HTML:\n" + html[:3000]

send_telegram(output)
