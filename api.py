from random import randint
import json
import arrow

from flask import Flask, request, jsonify, Response

from FlowrouteMessagingLib.Controllers.APIController import APIController
from FlowrouteMessagingLib.Models import Message

from settings import (DEBUG_MODE, CODE_LENGTH, CODE_EXPIRATION,
                      COMPANY_NAME, TEST_DB, DB, RETRIES_ALLOWED)

from credentials import (FLOWROUTE_ACCESS_KEY, FLOWROUTE_SECRET_KEY,
                         FLOWROUTE_NUMBER)
from storage import SQLiteAuthBackend, CodeNotSetError, InternalStorageError


app = Flask(__name__)
controller = APIController(username=FLOWROUTE_ACCESS_KEY,
                           password=FLOWROUTE_SECRET_KEY)
if DEBUG_MODE:
    app.debug = DEBUG_MODE
    storage = SQLiteAuthBackend(TEST_DB)
else:
    storage = SQLiteAuthBackend(DB)


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def generate_code(length=CODE_LENGTH):
    assert length > 0
    min_range = (10 ** (length - 1)) - 1
    max_range = (10 ** (length)) - 1
    code = randint(min_range, max_range)
    return code


def is_code_valid(timestamp, exp_window=CODE_EXPIRATION):
    now = arrow.utcnow()
    entry_time = arrow.get(timestamp)
    # When replace recieves pluralized kwarg it shifts (offset)
    exp_time = entry_time.replace(seconds=exp_window)
    if now <= exp_time:
        return True
    else:
        return False


@app.route("/", methods=['POST', 'GET'])
def user_verification():
    if request.method == 'POST':
        body = request.json
        session_id = str(body['auth_id'])
        recipient = int(body['recipient'])
        auth_code = generate_code()
        storage.set_auth_code(session_id, auth_code)
        msg = Message(
            to=recipient,
            from_=FLOWROUTE_NUMBER,
            content=("{}\n"
                     "Welcome to {}! Use this one-time code to "
                     "complete your sign up.").format(auth_code,
                                                      COMPANY_NAME))
        controller.create_message(msg)
        return "Verification code created."
    if request.method == 'GET':
        try:
            auth_id = str(request.args['auth_id'])
            query_code = int(request.args['code'])
        except:
            raise InvalidAPIUsage()
        try:
            stored_code, timestamp, attempts = storage.get_auth_code(auth_id)
        except storage.CodeNotSetError:
            # Likely the attempt threshold, or expirationm was reached
            return Response(
                json.dumps({"Authenticated": False, "Retry": False}),
                mimetype='application/json')
        is_valid = is_code_valid(timestamp)
        if is_valid:
            # Code has not expired
            if query_code == stored_code:
                    storage.delete_auth_code(auth_id)
                    return Response(
                        json.dumps({"Authenticated": True, "Retry": False}),
                        mimetype='application/json')
            else:
                if (attempts + 1) >= RETRIES_ALLOWED:
                    # That was the last try so remove the code
                    storage.delete_auth_code(auth_id)
                    return Response(
                        json.dumps({"Authenticated": False, "Retry": False}),
                        mimetype='application/json')
                else:
                    # Increment the attempts made
                    storage.set_num_attempts(auth_id, attempts + 1)
                    return Response(
                        json.dumps({"Authenticated": False, "Retry": True}),
                        mimetype='application/json')
        else:
            # Code has expired
            storage.delete_auth_code(auth_id)
            return Response(
                json.dumps({"Authenticated": False, "Retry": False}),
                mimetype='application/json')


@app.errorhandler(InternalStorageError)
def handle_database_error(error):
    response = jsonify({})
    response.status_code = 500
    return response


@app.errorhandler(CodeNotSetError)
def handle_not_found(error):
    response = jsonify({})
    response.status_code = 404
    return response


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == "__main__":
    app.run('127.0.0.1')
