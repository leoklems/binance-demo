from dataclasses import dataclass
from binance.spot import Spot
import typing


@dataclass
class BinanceService:
    api_key: typing.Optional[str] = ""
    api_secret: typing.Optional[str] = ""
    is_dev: typing.Optional[bool] = False

    @property
    def client(self):
        if self.is_dev:
            return Spot(base_url="https://testnet.binance.vision")
        if not self.api_key or not self.api_secret:
            raise Exception("api_key and api_secret must be set")
        return Spot(api_key=self.api_key, api_secret=self.api_secret)
    
    
