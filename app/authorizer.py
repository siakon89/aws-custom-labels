"""
Helper module for request authentication
"""
API_KEY = "<your custom api key>"


def is_authorized(headers):
    """
    Verify that a request contains the correct API key
    """
    return headers.get("x-api-key", "") == API_KEY or headers.get("X-Api-Key", "") == API_KEY
