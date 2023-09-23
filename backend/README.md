This is the server side of the stock data project. It will send dummy OHLC data relative to the current time. It's built with Fask and Socket.io

## Getting Started

First, setup the virtual environment

```bash
# Make sure you have virtualenv installed
virtualenv venv

.source/bin/activate # On Linux and Mac

venv\Scripts\activate
```

Now, install the requirements in our virtual environment

```bash
pip install -r requirements.txt
```

## Building and Running the project

Build and run the project in development mode:

```bash
python3 main.py
# or
python main.py
```

The project will run on the link "https"//localhost:5000". Use this to fetch the data from ur
WebSockets and flask server.

Make sure to create a `alpha_vantage_data` directory in the root bckend.

## Key Storage

Generate a RSA key and a CRT certificate as a .pem file and place it inside .secure/ folder. Without these files, the server won't start
