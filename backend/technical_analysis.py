import os
import requests
import pandas as pd
from error import ErrorKind
from dotenv import load_dotenv
import datetime

load_dotenv()

# Replace with your Alpha Vantage API key
API_KEY = os.environ.get('ALPHA_VANTAGE_API')

# Define the directory where you want to store the data
DATA_DIR = 'alpha_vantage_data'

US_ET_TZ = datetime.timezone(datetime.timedelta(hours=-4))  # Eastern Time (ET)
INDIA_TZ = datetime.timezone(datetime.timedelta(
    hours=5, minutes=30))  # India Standard Time (IST)


def ensure_data_directory_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def get_intraday_dummy_data(symbol, interval, date):
    """
    Fetches dummy intraday OHLCV data from Alpha Vantage API for a specific date.
    """

    try:
        # Change the cur timezone to US or India for testing purposes
        cur_time = datetime.datetime.now(INDIA_TZ)

        stock_data = get_intraday_data(symbol, interval, date)
        if isinstance(stock_data, ErrorKind):
            return stock_data

        # Filter stock data based on timestamps, ignoring the date
        filtered_data = stock_data[stock_data.index.time <= cur_time.time()]

        return filtered_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return ErrorKind.API_ERROR


def get_intraday_data(symbol, interval, date):
    """
    Fetches intraday OHLCV data from Alpha Vantage API for a specific date.

    Args:
    - symbol (str): The stock symbol (e.g., 'IBM').
    - interval (str): The interval for intraday data (e.g., '5min').
    - date (str): The date for which data is requested in the format 'YYYY-MM-DD'.

    Returns:
    - pd.DataFrame: A DataFrame containing OHLCV data for the specified date.
    """
    try:
        # Check if data for this month has already been fetched
        month = date[:7]
        month_folder = os.path.join(DATA_DIR, month)
        data_file = os.path.join(month_folder, f'{symbol}_{date}.csv')

        if os.path.exists(data_file):
            # Data already exists, load and return it
            df = pd.read_csv(data_file, parse_dates=True)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Set 'timestamp' as the index
            df.set_index('timestamp', inplace=True)
            df.index.name = None  # Clear the index name
            return df

        # Data does not exist, fetch it from Alpha Vantage
        ensure_data_directory_exists()
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&month={month}&outputsize=full&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        # Check if Alpha Vantage returned an error
        if 'Error Message' in data:
            print(f'Error fetching data for {symbol}')
            return ErrorKind.API_ERROR

        # Convert data to a DataFrame
        if 'Time Series (1min)' in data:
            df = pd.DataFrame(data['Time Series (1min)']).T
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)

            # Filter data based on date
            filtered_data = df[df.index.date == pd.to_datetime(date).date()]
            if filtered_data.empty:
                return ErrorKind.INVALID_DATE

            # Save the data to a CSV file for future use
            if not os.path.exists(month_folder):
                os.makedirs(month_folder)
            filtered_data.to_csv(data_file, index_label='timestamp')

            return filtered_data
        else:
            print(f'Error fetching data for {symbol}')
            return ErrorKind.MISSING_DATA
    except Exception as e:
        print(f"An error occurred: {e}")
        return ErrorKind.API_ERROR


def calculate_sma(data, window=14):
    """
    Calculates Simple Moving Average (SMA) for a given DataFrame.

    Args:
    - data (pd.DataFrame): DataFrame with 'close' prices.
    - window (int): The window size for calculating the SMA.

    Returns:
    - pd.Series: Series containing SMA values.
    """
    try:
        sd = data['close'].rolling(window=window).mean()
        return sd
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def calculate_ema(data, span=14):
    """
    Calculates Exponential Moving Average (EMA) for a given DataFrame.

    Args:
    - data (pd.DataFrame): DataFrame with 'close' prices.
    - span (int): The span for calculating the EMA.

    Returns:
    - pd.Series: Series containing EMA values.
    """
    try:
        return data['close'].ewm(span=span, adjust=False).mean()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def calculate_rsi(data, window=14):
    """
    Calculates Relative Strength Index (RSI) for a given DataFrame.

    Args:
    - data (pd.DataFrame): DataFrame with 'close' prices.
    - window (int): The window size for calculating the RSI.

    Returns:
    - pd.Series: Series containing RSI values.
    """
    try:
        price_diff = data['close'].diff()
        gain = price_diff.where(price_diff > 0, 0)
        loss = -price_diff.where(price_diff < 0, 0)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
