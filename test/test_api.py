import pytest
import os
import json
import urllib
import arrow
from ..api import generate_code, is_code_valid, app
from ..settings import TEST_DB, RETRIES_ALLOWED
from ..storage import SQLiteAuthBackend
from test_storage import test_set_code


def teardown_module(module):
    os.remove(TEST_DB)


@pytest.mark.parametrize("length, err", [
    (-1, AssertionError),
    (0, AssertionError),
    (1, None),
    (2, None),
    (3, None),
    (4, None),
    (5, None),
    (10, None),
])
def test_generate_code(length, err):
    if err:
        with pytest.raises(err):
            generate_code(length)
    else:
        code = generate_code(length)
        assert type(code) == int
        assert len(str(code)) == length


@pytest.mark.parametrize("ts, exp_window, expected", [
    (str(arrow.utcnow()), 10, True),
    (str(arrow.utcnow()), 0, False),
    (str(arrow.utcnow().replace(seconds=-60)), 60, False),
])
def test_is_code_valid(ts, exp_window, expected):
    res = is_code_valid(ts, exp_window=exp_window)
    assert res is expected

#
#def test_post_auth(app=app):
#    client = app.test_client()
#    auth_uuid = str(uuid.uuid1())
#    json_body = {"auth_id": auth_uuid}
#    length = len(json.dumps(json_body))
#    res = client.post('/', data=json_body,
#                      content_type='application/json',
#                      content_length=length)
#    assert res.status_code == 200


def test_get_auth_success(app=app):
    client = app.test_client()
    auth_uuid = test_set_code()
    backend = SQLiteAuthBackend(database_name=TEST_DB)
    backend.set_num_attempts(auth_uuid, RETRIES_ALLOWED - 1)
    query = urllib.urlencode(
        {'auth_id': auth_uuid,
         'code': 1234,
         })
    with client:
        res = client.get('/?' + query)
    assert res.status_code == 200
    assert json.loads(res.data)['Authenticated'] is True


@pytest.mark.parametrize("retries, retry", [
    (RETRIES_ALLOWED - 1, False),
    (1, True),
])
def test_get_auth_attempts_fail(retries, retry, app=app):
    client = app.test_client()
    auth_uuid = test_set_code()
    backend = SQLiteAuthBackend(database_name=TEST_DB)
    backend.set_num_attempts(auth_uuid, retries)
    query = urllib.urlencode(
        {'auth_id': auth_uuid,
         'code': 1111,
         })
    with client:
        res = client.get('/?' + query)
    assert res.status_code == 200
    assert json.loads(res.data)['Authenticated'] is False
    assert json.loads(res.data)['Retry'] is retry
