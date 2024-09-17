from starlette.applications import Starlette
from starlette.responses import JSONResponse
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

async def balance(request):
    account_info = service.client.get_account()
    return JSONResponse(account_info)

async def history(request):
    # trades = service.client.get_open_orders(symbol="BTCUSDT")
    trades = service.get_trade_history(symbol="BTCUSDT")
    print("Trade Open:", trades)
    return JSONResponse(trades)

# Function to place a market order
def place_market_order(symbol='BTCUSDT', quantity=0.01, side=SIDE_BUY):
    endpoint = '/order'
    url = base_url + endpoint

    # Debugging logs
    print(f"Symbol: {symbol}, Quantity: {quantity}, Side: {side}")

    data = {
        'symbol': symbol,
        'side': side,
        'type': 'MARKET',
        'quantity': quantity,
        'timestamp': int(time.time() * 1000)
    }

    query_string = '&'.join([f"{key}={value}" for key, value in data.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    data['signature'] = signature

    print(data)

    headers = {
        'X-MBX-APIKEY': api_key,
        "Content-Type": "application/json"
    }
    
    print("headers : ", headers)
    response = requests.post(url, headers=headers, json=data)
    print("response parsed")

    if response.content:
        print("we have content")
        try:
            response_json = response.json()
            print("we have json response")
            return response_json
        except requests.exceptions.JSONDecodeError as e:
            return {"error": "Failed to decode JSON", "details": str(e)}
    else:
        return {"error": "Empty response received."}


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

app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/order/", order_page),  # Route for rendering order page
        Route("/account/", balance),
        Route("/history/", history),
        Route('/order/submit', order_endpoint, methods=["POST"]),  # Separate route for POST request
    ],
)


# Key Changes:
# Route Change: The /order/ route now correctly points to the order_endpoint function.
# requests.post() Call: The data is passed as json=data, ensuring proper JSON serialization.
# Balance Endpoint: The balance function returns a JSON response to ensure the client receives it correctly.