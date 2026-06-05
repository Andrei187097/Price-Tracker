import requests
from bs4 import BeautifulSoup
import os
import json

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
URL = 'https://www.hsnstore.com/marcas/sport-series/evowhey-protein'
PRICE_FILE = 'last_price.json'

TARGET_WEIGHTS = ['500g', '2kg']  # Ajusta si los labels exactos son distintos

def deep_find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            result = deep_find(v, key)
            if result is not None:
                return result
    return None

def get_prices():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    response = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    json_config = None
    swatch_config = None

    for script in soup.find_all('script', type='text/x-magento-init'):
        try:
            data = json.loads(script.string)
            jc = deep_find(data, 'jsonConfig')
            if jc:
                json_config = jc
            sc = deep_find(data, 'jsonSwatchConfig')
            if sc:
                swatch_config = sc
        except Exception:
            pass

    if not json_config or not swatch_config:
        return None

    # Mapear label -> option_id desde el swatch config
    option_to_label = {}
    weight_attr_id = None

    for attr_id, options in swatch_config.items():
        if not isinstance(options, dict):
            continue
        for opt_id, opt_data in options.items():
            if not isinstance(opt_data, dict):
                continue
            label = opt_data.get('label', '')
            if label in TARGET_WEIGHTS:
                weight_attr_id = attr_id
                option_to_label[opt_id] = label

    if not weight_attr_id or not option_to_label:
        return None

    # Cruzar con precios del jsonConfig
    option_prices = json_config.get('optionPrices', {})
    index = json_config.get('index', {})

    prices = {}
    for product_id, attrs in index.items():
        opt_id = attrs.get(weight_attr_id)
        if opt_id in option_to_label and product_id in option_prices:
            label = option_to_label[opt_id]
            price = option_prices[product_id]['finalPrice']['amount']
            prices[label] = f"{price:.2f} €"

    return prices if prices else None

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
            msg = f'💰 <b>¡Cambio de precio EvoWhey!</b>\n\n' + '\n'.join(changes) + f'\n\n{URL}'
            send_telegram(msg)

    save_prices(current_prices)
