import requests
from bs4 import BeautifulSoup
import os
import json

# Los secretos los configuraremos luego en GitHub, no van aquí en el código
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

URL = 'https://www.hsnstore.com/marcas/sport-series/evowhey-protein'
PRICE_FILE = 'last_price.json'

def get_price():
    # Simulamos headers de un navegador real para esquivar el anti-bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    response = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Probamos varios selectores típicos de tiendas Magento (como HSN)
    price = soup.select_one('[data-price-type="finalPrice"] .price')
    if not price:
        price = soup.select_one('.special-price .price')
    if not price:
        price = soup.select_one('.price')

    return price.text.strip() if price else None

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'})

def load_last_price():
    # Lee el precio guardado de la última ejecución
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, 'r') as f:
            return json.load(f).get('price')
    return None

def save_price(price):
    with open(PRICE_FILE, 'w') as f:
        json.dump({'price': price}, f)

# --- Lógica principal ---
current_price = get_price()

if not current_price:
    send_telegram('⚠️ <b>Price Tracker:</b> No se pudo leer el precio. La web puede haber cambiado.')
else:
    last_price = load_last_price()

    if last_price is None:
        # Primera vez que corre: guarda el precio y avisa
        send_telegram(f'✅ <b>Price Tracker iniciado</b>\nPrecio actual del EvoWhey: <b>{current_price}</b>')
    elif current_price != last_price:
        # Hubo un cambio: avisa con el antes y el después
        send_telegram(f'💰 <b>¡Cambio de precio!</b>\nAntes: {last_price}\nAhora: <b>{current_price}</b>\n\n{URL}')
    # Si no hay cambio, no hace nada (no te spamea)

    save_price(current_price)
