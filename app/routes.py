from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from service.binance_service import BinanceService
from binance.client import Client
from settings import BINANCE_API_KEY, BINANCE_API_SECRET, DEBUG
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from threading import Thread
import time
import hmac 
import hashlib
import requests
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import (
    AuthenticationBackend, AuthCredentials, SimpleUser, requires
)
from starlette.authentication import requires
import bcrypt
import uvicorn
import sqlite3

# from routes import routes as routes

# Database setup
def get_db_connection():
    conn = sqlite3.connect('my.db')
    conn.row_factory = sqlite3.Row
    return conn

# User registration
async def register(request):
    if request.method == 'POST':
        form = await request.form()
        username = form['username']
        email = form['email']
        password = form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
        conn.commit()
        conn.close()

        return RedirectResponse(url='/', status_code=303)
    return templates.TemplateResponse('register.html', {'request': request})

# User login
async def login(request):
    if request.method == 'POST':
        form = await request.form()
        username = form['username']
        password = form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            request.session['user'] = username
            return RedirectResponse(url='/', status_code=303)
        else:
            return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid credentials'})

    return templates.TemplateResponse('login.html', {'request': request})


api_key = BINANCE_API_KEY
api_secret = BINANCE_API_SECRET

# Binance API base URL for the Testnet
base_url = 'https://testnet.binance.vision/api/v3'

service = BinanceService(
    api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET, is_dev=DEBUG
)

client = Client(
    api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET, testnet=True
)

# Setup the template directory
templates = Jinja2Templates(directory="templates")

# @requires('authenticated')
async def homepage(request):
    return templates.TemplateResponse('home.html', {'request': request, 'user': request.session.get('user')})

async def order_page(request):
    return templates.TemplateResponse("order.html", {"request": request})

async def btc_pricing_page(request):
    return templates.TemplateResponse("btc_pricing_form.html", {"request": request})

async def balance(request):
    account_info = service.get_account_details()
    return JSONResponse(account_info)

async def history(request):
    # trades = service.client.get_open_orders(symbol="BTCUSDT")
    trades = service.get_trade_history(symbol="BTCUSDT")
    print("Trade Open:", trades)
    return JSONResponse(trades)

async def open_orders(request):
    # trades = service.client.get_open_orders(symbol="BTCUSDT")
    trades = service.get_open_orders(symbol="BTCUSDT")
    print("Trade Open:", trades)
    return JSONResponse(trades)


async def order_endpoint(request):
    try:
        if request.headers.get('content-type') == 'application/json':
            body = await request.json()
        else:
            body = await request.form()

        symbol = body.get('symbol', 'BTCUSDT')
        quantity = float(body.get('quantity', 0.01))
        side = body.get('side', 'BUY').upper()

        # Debugging logs
        print(f"Symbol: {symbol}, Quantity: {quantity}, Side: {side}")

        # Validate input parameters
        if not symbol or not quantity or not side:
            return JSONResponse({'error': 'Missing required parameters'}, status_code=400)

        # Map side to Binance enums
        side_enum = SIDE_BUY if side == 'BUY' else SIDE_SELL

        # Place the order using BinanceService
        order_response = service.place_order(
            symbol=symbol,
            side=side_enum,
            order_type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        # Return the order response as JSON
        return JSONResponse(order_response)

    except Exception as e:
        print(f"Error placing order: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

async def fetch_prices(request):
    try:
        form = await request.form()

        symbol = 'BTCUSDT'
        interval = Client.KLINE_INTERVAL_1DAY  # 1 day interval
        start_date = form['start_date']
        end_date = form['end_date']

        # Debugging logs
        print(f"Symbol: {symbol}, start_date: {start_date}, end_date: {end_date}")

        # Validate input parameters
        if not symbol or not start_date or not end_date:
            return JSONResponse({'error': 'Missing required parameters'}, status_code=400)

        # Place the order using BinanceService
        order_response = service.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_date,
            end_str=end_date
        )

        # Return the order response as JSON
        return HTMLResponse(order_response.to_html())

    except Exception as e:
        print(f"Error placing order: {e}")
        return JSONResponse({'error': str(e)}, status_code=500)

    # form = await request.form()
    # start_date = form['start_date']
    # end_date = form['end_date']

async def start_kline_stream(request):
    symbol = request.path_params['symbol']
    interval = request.path_params['interval']
    print(f"Received request to start kline stream for {symbol} with interval {interval}")
    thread = Thread(target=service.start_kline_stream, args=(symbol, interval))
    thread.start()
    return JSONResponse({"message": f"Started Kline stream for {symbol} with interval {interval}"})



async def logout(request):
    request.session.clear()
    return RedirectResponse(url='/login', status_code=303)

routes = [
    Route('/register', register, methods=['GET', 'POST']),
    Route('/login', login, methods=['GET', 'POST']),
    Route("/", homepage),
    Route("/order/", order_page),  # Route for rendering order page
    Route("/pricing/", btc_pricing_page),  # Route for rendering order page
    Route("/account/", balance),
    Route("/history/", history),
    Route("/open-orders/", open_orders),
    Route('/order/submit', order_endpoint, methods=["POST"]),  # Separate route for POST request
    Route('/fetch_prices', endpoint=fetch_prices, methods=['POST']),
    Route('/start_kline_stream/{symbol:str}/{interval:str}', start_kline_stream),
]
