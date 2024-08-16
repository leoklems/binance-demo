from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from service.binance_service import BinanceService
from binance.client import Client
from settings import BINANCE_API_KEY, BINANCE_API_SECRET, DEBUG
from binance.enums import SIDE_BUY, ORDER_TYPE_MARKET
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

async def homepage(request):
    return JSONResponse({"hello": "world"})

async def balance(request):
    return client.get_account()

# Function to place a market order
# def place_market_order(symbol, quantity, side):
# def place_market_order(symbol, quantity, side):
def place_market_order(symbol='BTCUSDT', quantity=0.01, side=SIDE_BUY):

    endpoint = '/order'
    url = base_url + endpoint

    # Create a payload with the necessary parameters
    data = {
        'symbol': 'BTCUSDT',
        'side': side,
        'type': 'MARKET',
        'quantity': quantity,
        'timestamp': int(time.time() * 1000)
    }

    # Create a signature using HMAC SHA256
    query_string = '&'.join([f"{key}={value}" for key, value in data.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Add the signature to the data
    data['signature'] = signature

    # Add headers
    headers = {
        'X-MBX-APIKEY': api_key,
        "Content-Type": "application/json"
    }
    
    print("stuff added", data)
    # Send the request
    response = requests.post(url, headers=headers, data=data)
    print("response",response)

    # Only try to parse as JSON if the content is not empty
    if response.content:
        try:
            response_json = response.json()
            print("Response JSON:", response_json)
            
            return response_json
        except requests.exceptions.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
    else:
        print("Empty response received.")
        # Return the response JSON
    return response.json()
    # return response


# Endpoint to handle POST request and place a market order
async def order_endpoint(request):
    try:
        # Parse the request body
        body = await request.json()
        symbol = body.get('symbol')
        quantity = body.get('quantity')
        side = body.get('side')

        print(body)

        # Validate the inputs
        if not symbol or not quantity or not side:
            return JSONResponse({'error': 'Missing required parameters'}, status_code=400)

        # Interact with Binance API (ensure this part is correct)
        order_response = place_market_order(symbol, quantity, side)  # This function should interact with Binance

        return JSONResponse(order_response)
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/account/", balance),
        Route('/order/', place_market_order),
    ],
)
