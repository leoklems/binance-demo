from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
# from app import app
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import (
    AuthenticationBackend, AuthCredentials, SimpleUser, requires
)
import os
import logging
from routes import routes as routes
import secrets

# Set up logging
logging.basicConfig(level=logging.DEBUG)

secret_key = secrets.token_urlsafe(32)

# Add the SessionMiddleware first
# app.add_middleware(SessionMiddleware, secret_key=secret_key)
# logging.debug("SessionMiddleware added")


# Define a simple authentication backend
class SimpleAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if "user" in request.session:
            username = request.session["user"]
            # Add logic to verify the user's credentials
            if self.verify_credentials(username):  # Replace with your own verification logic
                return AuthCredentials(["authenticated"]), SimpleUser (username)
        return AuthCredentials([]), None

    def verify_credentials(self, username):
        # Replace with your own verification logic
        # For example, you could check a database to see if the username exists
        # or if the username and password match
        return True  # Replace with your own verification logic
    
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