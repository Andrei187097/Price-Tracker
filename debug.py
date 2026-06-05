import requests
from bs4 import BeautifulSoup
import json

URL = 'https://www.hsnstore.com/marcas/sport-series/evowhey-protein'

def deep_find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            result = deep_find(v, key)
            if result is not None:
                return result
    return None

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9',
}
response = requests.get(URL, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

for script in soup.find_all('script', type='text/x-magento-init'):
    try:
        data = json.loads(script.string)
        sc = deep_find(data, 'jsonSwatchConfig')
        jc = deep_find(data, 'jsonConfig')

        if sc:
            print("=== jsonSwatchConfig ===")
            print(json.dumps(sc, indent=2, ensure_ascii=False))
        if jc:
            print("=== jsonConfig (optionPrices) ===")
            print(json.dumps(jc.get('optionPrices', {}), indent=2, ensure_ascii=False))
            print("=== jsonConfig (index) ===")
            print(json.dumps(jc.get('index', {}), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Script ignorado: {e}")
