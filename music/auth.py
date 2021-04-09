import requests, logging, time
from .utils import getproperty
from requests.auth import HTTPBasicAuth

class Auth():
    logger = logging.getLogger("auth")

    auth_server_url = None
    client_id = None
    client_secret = None
    grant_type = None
    access_token = None
    access_token_expiration = None

    def __init__(self):
        self.auth_server_url = getproperty('auth', 'url')
        self.client_id = getproperty('auth', 'client_id')
        self.client_secret = getproperty('auth', 'client_secret')
        self.grant_type = getproperty('auth', 'grant_type')

        self.get_access_token()
        if self.access_token is None:
            self.logger.error("Request for access token failed")

    def get_access_token(self):
        payload = {
            'grant_type': self.grant_type
        }
        response = requests.post(self.auth_server_url + '/token', auth=HTTPBasicAuth(self.client_id, self.client_secret), data=payload)
        if response.status_code == 400:
            self.logger.error(self, 'Error retrieving token', response.json())

        json = response.json()
        self.access_token = json.get('access_token')
        self.access_token_expiration = time.time() + json.get("expires_in")
        return self.access_token

    # class Decorators():
    #     @staticmethod
    #     def refresh_token(decorated):
    #         def wrapper(auth, *args, **kwargs):
    #             if time.time() > auth.access_token_expiration:
    #                 auth.get_access_token()
    #             return decorated(auth, *args, **kwargs)
    #         return wrapper