"""
FinDB auth utils
"""

from base64 import b64encode
from os import environ

from requests import post

CONSUMER_KEY = environ["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = environ["TWITTER_CONSUMER_SECRET"]

COMBINED_KEY = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"

REQUEST_BEARER_TOKEN = b64encode(
    bytes(
        f"{COMBINED_KEY}",
        encoding="utf-8",
    )
).decode("utf-8")

ACCESS_TOKEN = None


def get_access_token() -> str:
    """
    Generates and returns an Access token
    """
    # pylint: disable=global-statement
    global ACCESS_TOKEN

    if ACCESS_TOKEN is None:
        res = post(
            url="https://api.twitter.com/oauth2/token",
            data="grant_type=client_credentials",
            headers={
                "Authorization": f"Basic {REQUEST_BEARER_TOKEN}",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            },
            timeout=30,
        ).json()

        ACCESS_TOKEN = res["access_token"]

    return ACCESS_TOKEN
