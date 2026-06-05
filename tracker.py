import requests
import re
import json
import os

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
URL = 'https://www.hsnstore.com/marcas/sport-series/evowhey-protein'
PRICE_FILE = 'last_price.json'

# option_id -> label (extraído del debug, no cambian salvo rediseño de HSN)
TARGET_OPTIONS = {
    '1854': '500g',
    '3486': '2Kg',
}

def get_prices():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    response = requests.get(URL, headers=headers, timeout=10)
    html = response.text

    # Extraer el índice del atributo 216: {"opt_id": ["prod_id", ...], ...}
    attr_match = re.search(r'"216":\{((?:"[\d]*":\[[^\]]*\],?)+)\}', html)
    if not attr_match:
        return None

    option_map = {}
    for m in re.finditer(r'"(\d+)":\[([^\]]*)\]', attr_match.group(1)):
        opt_id = m.group(1)
        products = re.findall(r'"(\d+)"', m.group(2))
        option_map[opt_id] = products

    result = {}
    for opt_id, label in TARGET_OPTIONS.items():
        products = option_map.get(opt_id, [])
        if not products:
            continue
        # Cogemos el primer producto de esa opción (todos del mismo tamaño tienen igual precio)
        pid = products[0]
        price_match = re.search(rf'"{pid}":\{{[^}}]*"finalPrice":\{{"amount":([\d.]+)', html)
        if price_match:
            result[label] = f"{float(price_match.group(1)):.2f} €"

    return result if result else None

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'})

def load_last_prices():
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_prices(prices):
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f)

# --- Lógica principal ---
current_prices = get_prices()

if not current_prices:
    send_telegram('⚠️ <b>Price Tracker:</b> No se pudieron leer los precios. La web puede haber cambiado.')
else:
    last_prices = load_last_prices()

    if not last_prices:
        msg = '✅ <b>Price Tracker iniciado</b>\n'
        for label, price in current_prices.items():
            msg += f'\n• EvoWhey {label}: <b>{price}</b>'
        send_telegram(msg)
    else:
        changes = []
        for label, price in current_prices.items():
            old = last_prices.get(label)
            if old and old != price:
                changes.append(f'• EvoWhey {label}: {old} → <b>{price}</b>')
        if changes:
            msg = '💰 <b>¡Cambio de precio EvoWhey!</b>\n\n' + '\n'.join(changes) + f'\n\n{URL}'
            send_telegram(msg)

    save_prices(current_prices)
