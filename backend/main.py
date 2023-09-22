# main.py

import json
from technical_analysis import get_intraday_data, calculate_sma, calculate_ema, calculate_rsi
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import datetime
from error import ErrorKind

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure SSL/TLS certificate and key paths
ssl_cert_path = '/.secure/tls_cert.crt'
ssl_key_path = '/.secure/tls_key.key'

SYMBOL = 'IBM'
INTERVAL = '5min'
SLEEP_TIME = 60


def calculate_intraday_data(date):
    # Attempt to fetch intraday data
    data = get_intraday_data(SYMBOL, INTERVAL, date)

    # Check for error from get_intraday_data
    if isinstance(data, ErrorKind):
        return data  # Propagate the error

    try:
        ohlc = data[['open', 'high', 'low', 'close', 'volume']].copy()
        ohlc['timestamp'] = ohlc.index.astype(str)
        ohlc_dict = ohlc.to_dict(orient='records')
        sma = calculate_sma(data).iloc[-1]
        ema = calculate_ema(data).iloc[-1]
        rsi = calculate_rsi(data).iloc[-1]

        stock_data = {
            "symbol": SYMBOL,
            "ohlc": ohlc_dict,
            "sma": sma,
            "ema": ema,
            "rsi": rsi
        }
        return stock_data

    except Exception as e:
        print(f'Error calculating intraday data: {e}')
        return ErrorKind.INTERNAL_ERROR  # You can define an appropriate error type


def send_stock_data():
    current_date = datetime.datetime.now()

    # Alpha Vantage does not store the Intraday data for the current date.
    # So, we fetch the data for the previous date.
    yesterday = current_date - datetime.timedelta(days=1)

    # We'll traverse the date for the last 2 months and send the data to our API.
    # This will also help us in going in an infinite loop.
    while yesterday >= current_date - datetime.timedelta(days=60):
        date_to_fetch = yesterday.strftime('%Y-%m-%d')
        stock_data = calculate_intraday_data(date_to_fetch)

        # Check if the stock data exists for the given date,
        # if not, then fetch the data for the previous day
        if stock_data == ErrorKind.INVALID_DATE:
            yesterday -= datetime.timedelta(days=1)
            continue

        # If we get any other error, propagate it
        elif isinstance(stock_data, ErrorKind):
            return

        json_data = json.dumps(stock_data)

        socketio.emit('stock_data', json_data)
        # print(stock_data)

        yesterday -= datetime.timedelta(days=1)
        socketio.sleep(60)


socketio.start_background_task(send_stock_data)

if __name__ == '__main__':
    socketio.init_app(app, certfile=ssl_cert_path,
                      keyfile=ssl_key_path, ssl_version='TLSv1_2')
    socketio.run(app, host='127.0.0.1', port=8080,
                 debug=True, use_reloader=False)
