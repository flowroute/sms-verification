from random import randint
import json
import arrow
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from FlowrouteMessagingLib.Controllers.APIController import APIController
from FlowrouteMessagingLib.Models import Message

from settings import (DEBUG_MODE, CODE_LENGTH, CODE_EXPIRATION,
                      COMPANY_NAME, TEST_DB, DB, RETRIES_ALLOWED)

from credentials import (FLOWROUTE_ACCESS_KEY, FLOWROUTE_SECRET_KEY,
                         FLOWROUTE_NUMBER)
from log import log


app = Flask(__name__)
controller = APIController(username=FLOWROUTE_ACCESS_KEY,
                           password=FLOWROUTE_SECRET_KEY)
app.sms_controller = controller

if DEBUG_MODE:
    app.debug = DEBUG_MODE
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + TEST_DB
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB

db = SQLAlchemy(app)


class AuthCode(db.Model):
    auth_id = db.Column(db.String(120), primary_key=True)
    code = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    attempts = db.Column(db.Integer, default=0)

    def __init__(self, auth_id, code):
        self.auth_id = auth_id
        self.code = code
        self.timestamp = datetime.utcnow()


class InvalidAPIUsage(Exception):

    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class InvalidAttemptError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
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
    log.debug({"message": "generated code: {}".format(code)})
    return code


def is_code_valid(timestamp, exp_window=CODE_EXPIRATION):
    now = arrow.utcnow()
    entry_time = arrow.get(timestamp)
    # When replace receives pluralized, ie. 'seconds' kwarg it shifts (offset)
    exp_time = entry_time.replace(seconds=exp_window)
    if now <= exp_time:
        return True
    else:
        return False


@app.route("/", methods=['POST', 'GET'])
def user_verification():
    if request.method == 'POST':
        body = request.json
        auth_id = str(body['auth_id'])
        recipient = str(body['recipient'])
        auth_code = generate_code()
        # Just overwrite if exists
        auth = AuthCode(auth_id, auth_code)
        db.session.add(auth)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            update_info = {'code': auth_code,
                           'attempts': 0,
                           'timestamp': datetime.utcnow()}
            AuthCode.query.filter_by(
                auth_id=auth_id).update(update_info)
            db.session.commit()
        log.debug({"message": "persisted auth record"})
        msg = Message(
            to=recipient,
            from_=FLOWROUTE_NUMBER,
            content=("{}\n"
                     "Welcome to {}! Use this one-time code to "
                     "complete your sign up.").format(auth_code,
                                                      COMPANY_NAME))
        app.sms_controller.create_message(msg)
        log.info(
            {"message": "sent SMS with auth code to {}".format(recipient)})
        return "Verification code created."
    if request.method == 'GET':
        try:
            auth_id = str(request.args['auth_id'])
            query_code = int(request.args['code'])
        except:
            raise InvalidAPIUsage(payload={'requires': ['auth_id (str)',
                                                        'code (int)']})
            log.debug(
                {"message":
                 "received an auth request for id {}".format(auth_id)})
        try:
            stored_auth = AuthCode.query.filter_by(auth_id=auth_id).one()
        except NoResultFound:
            # Likely the attempt threshold, or expiration was reached
            log.info({"message": "no auth id found matching the request",
                      "auth_id": auth_id})
            raise InvalidAttemptError(
                "Unknown auth id",
                payload={'attempts_left': 0})
        else:
            stored_code = stored_auth.code
            timestamp = stored_auth.timestamp
            attempts = stored_auth.attempts
            is_valid = is_code_valid(timestamp)
        if is_valid:
            if query_code == stored_code:
                db.session.delete(stored_auth)
                db.session.commit()
                log.info({"message": "Success: Authorization code verified."})
                return Response(
                    json.dumps({"authenticated": True,
                                "message":
                                "Success: Authorization code verified."}),
                    mimetype='application/json')
            else:
                attempts_made = attempts + 1
                if attempts_made >= RETRIES_ALLOWED:
                    # That was the last try so remove the code
                    db.session.delete(stored_auth)
                    db.session.commit()
                    log.info({"reason": 'InvalidAuthCode',
                              "auth_id": auth_id,
                              "attempts_left": 0})
                    raise InvalidAttemptError(
                        "Invalid code",
                        payload={"reason": 'InvalidAuthCode',
                                 "attempts_left": 0})
                else:
                    num_left = (RETRIES_ALLOWED - attempts_made)
                    # Increment the attempts made
                    stored_auth.attempts = attempts_made
                    db.session.commit()
                    log.info({"reason": "InvalidAuthCode",
                              "auth_id": auth_id,
                              "attempts_left": num_left})
                    raise InvalidAttemptError(
                        "Invalid code",
                        payload={"message": "Invalid code",
                                 "reason": 'InvalidAuthCode',
                                 "attempts_left": 0})
        else:
            # Code has expired
            db.session.delete(stored_auth)
            db.session.commit()
            log.info({"message": "auth code has expired",
                      "auth_id": auth_id})
            raise InvalidAttemptError("Expired code",
                                      payload={'reason': 'ExpiredAuthCode',
                                               'attempts_left': 0})


@app.errorhandler((InvalidAPIUsage, InvalidAttemptError))
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == "__main__":
    db.create_all()
    app.run('127.0.0.1')
