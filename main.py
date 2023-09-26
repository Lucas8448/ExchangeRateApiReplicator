from flask import Flask, jsonify
import requests
import schedule
import time
from threading import Thread

app = Flask(__name__)

exchange_rates = {}

def fetch_exchange_rates():
    global exchange_rates
    api_key = "262a36b33262d887a482c003"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        exchange_rates = response.json()['conversion_rates']
    else:
        print(f"Failed to update exchange rates. HTTP Status Code: {response.status_code}")

schedule.every(2).hours.do(fetch_exchange_rates)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/latest/<string:base_currency>', methods=['GET'])
def get_exchange_rate(base_currency):
    if base_currency in exchange_rates:
        return jsonify({
            'result': 'success',
            'base_code': base_currency,
            'conversion_rates': {key: rate / exchange_rates[base_currency] for key, rate in exchange_rates.items()}
        })
    else:
        return jsonify({'result': 'error', 'message': f'Base currency {base_currency} not found'}), 400

if __name__ == '__main__':
    fetch_exchange_rates()
    t = Thread(target=run_schedule)
    t.start()
    app.run(port=5000)
