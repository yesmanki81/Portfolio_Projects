# crypto.py
import requests, time, json

def get_price(symbol='BTC', currency='USD'):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms={currency}"
    response = requests.get(url)
    return response.json()

while True:
    for coin in ['BTC', 'ETH']:
        price_data = get_price(coin)
        record = {
            'symbol': coin,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'price': price_data['USD']
        }
        print(record)
    time.sleep(120)