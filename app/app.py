import base64
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
# from index import SimpleAuthBackend
import logging
import secrets

secret_key = secrets.token_urlsafe(32)
print(secret_key)

app = Starlette(
    debug=True,
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

# Add the SessionMiddleware first
app.add_middleware(SessionMiddleware, secret_key=secret_key)
logging.debug("SessionMiddleware added")


# class SimpleAuthBackend(AuthenticationBackend):
#     async def authenticate(self, request):
#         if "user" in request.session:
#             username = request.session["user"]
#             # Add logic to verify the user's credentials
#             if self.verify_credentials(username):  # Replace with your own verification logic
#                 return AuthCredentials(["authenticated"]), SimpleUser (username)
#         return AuthCredentials([]), None

#     def verify_credentials(self, username):
#         # Replace with your own verification logic
#         # For example, you could check a database to see if the username exists
#         # or if the username and password match
#         return True  # Replace with your own verification logic

class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        auth = request.headers.get('Authorization')
        if auth:
            scheme, _, credentials = auth.partition(' ')
            if scheme.lower() == 'basic':
                # Decode the credentials and verify them
                username, password = base64.b64decode(credentials).decode().split(':', 1)
                if self.verify_credentials(username, password):
                    return AuthCredentials(['authenticated']), SimpleUser (username)
        return None

    def verify_credentials(self, username, password):
        # Replace this with your own verification logic
        return username == "admin" and password == "secret"
# Add the AuthenticationMiddleware
# app.add_middleware(AuthenticationMiddleware, backend=SimpleAuthBackend())
app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
logging.debug("AuthenticationMiddleware added")

# Define the routes
app.router.routes.extend(routes)


# Key Changes:
# Route Change: The /order/ route now correctly points to the order_endpoint function.
# requests.post() Call: The data is passed as json=data, ensuring proper JSON serialization.
# Balance Endpoint: The balance function returns a JSON response to ensure the client receives it correctly.