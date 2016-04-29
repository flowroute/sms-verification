import json

import requests


SMS_AUTH_ENDPOINT = 'http://localhost:5000'


class SMSAuthClient(object):

    def __init__(self, endpoint=SMS_AUTH_ENDPOINT):
        self.endpoint = endpoint

    def create_auth(self, auth_id, recipient):
        payload = {'auth_id': auth_id,
                   'recipient': recipient}
        response = requests.post(self.endpoint, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError, e:
            import pdb; pdb.set_trace()
            content = e.response.json()
            e.message = content['message']
            e.strerror = content['reason']
            raise e

        return response.json()

    def authenticate_code(self, auth_id, code):
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
