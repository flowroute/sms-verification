import json

import requests


SMS_AUTH_ENDPOINT = 'http://localhost:5000'


class SMSAuthClient(object):
    """
    A client for the SMS auth service that returns a JSON response, or
    raises exceptions containing helpful information (message, reason,
    attempts_left).

    Takes an HTTP endpoint as its only argument.
    """

    def __init__(self, endpoint=SMS_AUTH_ENDPOINT):
        self.endpoint = endpoint

    def create_auth(self, auth_id, recipient):
        """
        Posts the provided auth_id and recipient to the SMS auth service.
        Returns the JSON response, or raises a requests.exception.HTTPError
        with helpful values if a non-200 response code is received.
        """
        payload = {'auth_id': auth_id,
                   'recipient': recipient}
        response = requests.post(self.endpoint, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError, e:
            content = e.response.json()
            e.message = content['message']
            e.strerror = content['reason']
            raise e

        return response.json()

    def authenticate_code(self, auth_id, code):
        """
        Requests authorization from the SMS auth service given the auth_id,
        and code (user input). Returns the response JSON, or raises a
        requests.exception.HTTPError with helpful values if a non 200
        response code is received.
        """
        args = {'auth_id': auth_id,
                'code': code}
        response = requests.get(self.endpoint, params=args)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError, e:
            content = e.response.json()
            e.message = content['message']
            e.strerror = content['reason']
            try:
                e.attempts_left = content['attempts_left']
            except:
                pass
            raise e
        return response.json()
