import time

def refresh_token(decorated):
    def wrapper(auth, *args, **kwargs):
        if time.time() > auth.access_token_expiration:
            auth.get_access_token()
        return decorated(auth, *args, **kwargs)

    return wrapper