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
import os
from routes import routes as routes

secret_key = os.urandom(24)

# # Define a simple authentication backend
# class SimpleAuthBackend(AuthenticationBackend):
#     async def authenticate(self, request):
#         if "user" in request.session:
#             return AuthCredentials(["authenticated"]), SimpleUser(request.session["user"])
#         return AuthCredentials([]), None



app = Starlette(
    debug=True,
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
# app.add_middleware(SessionMiddleware, secret_key=secret_key)
# app.add_middleware(AuthenticationMiddleware, backend=SimpleAuthBackend())
# app.router.routes.extend(routes)
# @app.route('/logout')
# async def logout(request):
#     request.session.clear()
#     return RedirectResponse(url='/login', status_code=303)


# Key Changes:
# Route Change: The /order/ route now correctly points to the order_endpoint function.
# requests.post() Call: The data is passed as json=data, ensuring proper JSON serialization.
# Balance Endpoint: The balance function returns a JSON response to ensure the client receives it correctly.