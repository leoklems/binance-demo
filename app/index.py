from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from .service.binance_service import BinanceService
from .settings import BINANCE_API_KEY, BINANCE_API_SECRET, DEBUG


service = BinanceService(
    api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET, is_dev=DEBUG
)


async def homepage(request):
    return JSONResponse({"hello": "world"})


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
    ],
)
