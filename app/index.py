from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from service.binance_service import BinanceService
from binance.client import Client
from settings import BINANCE_API_KEY, BINANCE_API_SECRET, DEBUG
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
import time
import hmac 
import hashlib
import requests

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

async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})

async def order_page(request):
    return templates.TemplateResponse("order.html", {"request": request})

async def btc_pricing_page(request):
    return templates.TemplateResponse("btc_pricing_form.html", {"request": request})

async def balance(request):
    account_info = service.client.get_account()
    return JSONResponse(account_info)

async def history(request):
    # trades = service.client.get_open_orders(symbol="BTCUSDT")
    trades = service.get_trade_history(symbol="BTCUSDT")
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

app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/order/", order_page),  # Route for rendering order page
        Route("/pricing/", btc_pricing_page),  # Route for rendering order page
        Route("/account/", balance),
        Route("/history/", history),
        Route('/order/submit', order_endpoint, methods=["POST"]),  # Separate route for POST request
        Route('/fetch_prices', endpoint=fetch_prices, methods=['POST']),
    ],
)


# Key Changes:
# Route Change: The /order/ route now correctly points to the order_endpoint function.
# requests.post() Call: The data is passed as json=data, ensuring proper JSON serialization.
# Balance Endpoint: The balance function returns a JSON response to ensure the client receives it correctly.