from dataclasses import dataclass
from binance.spot import Spot
import typing
import pandas as pd
import websocket
import json


@dataclass
class BinanceService:
    api_key: typing.Optional[str] = ""
    api_secret: typing.Optional[str] = ""
    is_dev: typing.Optional[bool] = False

    @property
    def client(self):
        # TestNet or Live environment
        if self.is_dev:
            return Spot(base_url="https://testnet.binance.vision", api_key=self.api_key, api_secret=self.api_secret)
        if not self.api_key or not self.api_secret:
            raise Exception("API key and API secret must be set")
        return Spot(api_key=self.api_key, api_secret=self.api_secret)

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: typing.Optional[float] = None):
        """Place a market or limit order"""
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }
        if order_type.lower() == "limit" and price:
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good 'til Cancelled

        try:
            print("The params are: ",params)
            response = self.client.new_order(**params)
            return response
        except Exception as e:
            print(f"Failed to place order: {e}")
            return None

    def get_trade_history(self, symbol: str):
        """Fetch trade history for a specific symbol"""
        try:
            trades = self.client.my_trades(symbol=symbol)
            return trades
        except Exception as e:
            print(f"Failed to fetch trade history: {e}")
            return None
    
    def get_open_orders(self, symbol: str):
        """Fetch trade history for a specific symbol"""
        try:
            trades = self.client.get_open_orders(symbol=symbol)
            return trades
        except Exception as e:
            print(f"Failed to fetch open orders: {e}")
            return None

    def get_account_details(self):
        """Fetch account details"""
        try:
            account = self.client.account()
            return  account
        except  Exception as e:
            print(f"Failed to fetch account details: {e}")
            return None
    
    # Fetch historical klines (candlestick data)
    def get_historical_klines(self, symbol, interval, start_str, end_str=None):
        klines = self.client.get_historical_klines(symbol, interval, start_str, end_str)
        # Convert to a DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ])
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def start_kline_stream(self, symbol: str, interval: str):
        """Start WebSocket connection for Kline stream"""
        def on_message(ws, message):
            data = json.loads(message)
            kline = data['k']
            is_kline_closed = kline['x']
            if is_kline_closed:
                kline_data = {
                    'timestamp': kline['t'],
                    'open': kline['o'],
                    'high': kline['h'],
                    'low': kline['l'],
                    'close': kline['c'],
                    'volume': kline['v']
                }
                print(kline_data)
                # You can also append this data to a DataFrame for further analysis
                # df = pd.DataFrame([kline_data])
                # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                # print(df)

        def on_error(ws, error):
            print(f"Error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket closed")

        def on_open(ws):
            print("WebSocket connection opened")

        ws_url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}"
        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()


