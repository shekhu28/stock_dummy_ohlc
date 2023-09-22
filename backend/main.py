import json
from technical_analysis import get_intraday_dummy_data, calculate_sma, calculate_ema, calculate_rsi
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from error import ErrorKind

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure SSL/TLS certificate and key paths
ssl_cert_path = '/.secure/tls_cert.crt'
ssl_key_path = '/.secure/tls_key.key'

symbol = 'IBM'
interval = '1min'
interval_secs = 60

# Store historical data and indicators for all stocks
stock_data = {}
latest_data = {}
last_timestamp = None


def calculate_initial_data(date):
    # Fetch and store initial data for all stocks
    global stock_data, last_timestamp
    data = get_intraday_dummy_data(symbol, interval, date)

    if isinstance(data, ErrorKind):
        return {"error": str(data)}  # Return error response

    ohlc = data[['open', 'high', 'low', 'close', 'volume']].copy()
    ohlc['timestamp'] = ohlc.index.astype(str)
    ohlc_dict = ohlc.to_dict(orient='records')
    sma = calculate_sma(data).iloc[-1]
    ema = calculate_ema(data).iloc[-1]
    rsi = calculate_rsi(data).iloc[-1]

    stock_data = {
        "symbol": symbol,
        "ohlc": ohlc_dict,
        "sma": sma,
        "ema": ema,
        "rsi": rsi
    }

    last_timestamp = data.index[0]
    return stock_data


def fetch_stock_prices():
    global stock_data, latest_data, last_timestamp
    while True:
        # Fetch and emit stock prices every minute
        socketio.sleep(interval_secs)
        data = get_intraday_dummy_data(symbol, interval, '2023-09-21')

        if isinstance(data, ErrorKind):
            print(f"Error fetching data: {data}")
            continue  # Skip this iteration if there was an error

        new_data = data[data.index > last_timestamp]
        if not new_data.empty:
            latest_data = new_data
            ohlc = new_data[['open', 'high', 'low', 'close', 'volume']].copy()
            ohlc['timestamp'] = ohlc.index.astype(str)
            ohlc_dict = ohlc.to_dict(orient='records')
            last_timestamp = new_data.index[0]
            sma = calculate_sma(data).iloc[-1]
            ema = calculate_ema(data).iloc[-1]
            rsi = calculate_rsi(data).iloc[-1]

            data_to_send = {
                "symbol": symbol,
                "ohlc": ohlc_dict,
                "sma": sma,
                "ema": ema,
                "rsi": rsi
            }

            json_data = json.dumps(data_to_send)

            # Send the new data to connected clients
            socketio.emit('new_data', json_data)


@app.route('/initial-data', methods=['GET'])
def send_initial_data_api():
    try:
        initial_data = calculate_initial_data('2023-09-21')
        if "error" in initial_data:
            # Return error response with status code 500
            return jsonify(initial_data), 500
        return jsonify(initial_data)
    except Exception as e:
        # Return error response with status code 500
        return jsonify({"error": str(e)}), 500


socketio.start_background_task(fetch_stock_prices)

if __name__ == '__main__':
    socketio.init_app(app, certfile=ssl_cert_path,
                      keyfile=ssl_key_path, ssl_version='TLSv1_2')
    socketio.run(app, host='127.0.0.1', port=8080,
                 debug=True, use_reloader=False)
