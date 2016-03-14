import pytest
import os
import sqlite3 as sqlite
import uuid
import arrow

from ..storage import SQLiteAuthBackend
from ..settings import TEST_DB


def teardown_module(module):
    os.remove(TEST_DB)


@pytest.fixture
def fresh_table():
    conn = sqlite.connect(TEST_DB)
    with conn:
        conn.execute('DROP TABLE IF EXISTS codes')
    return conn


def get_auth_data(cursor, auth_id):
    cursor.execute(
        "SELECT code, timestamp, attempts FROM codes WHERE auth_id = ?",
        (auth_id,))
    res = cursor.fetchone()
    cursor.close()
    return res


def test_create_table(fresh_table):
    backend = SQLiteAuthBackend(database_name=TEST_DB)
    cur = backend.db_conn.cursor()
    cur.execute("PRAGMA table_info([codes])")
    res = cur.fetchall()
    cur.close()
    assert 'auth_id' in res[0] and 'TEXT' in res[0]
    assert 'code' in res[1] and 'INTEGER' in res[1]
    assert 'timestamp' in res[2] and 'DATETIME' in res[2]
    assert 'attempts' in res[3] and 'INTEGER' in res[3]


def test_set_code():
    new_conn = fresh_table()
    backend = SQLiteAuthBackend(database_name=TEST_DB)
    auth_id = str(uuid.uuid1())
    backend.set_auth_code(auth_id, 1234)
    cur = new_conn.cursor()
    code, ts, attempts = get_auth_data(cur, auth_id)
    assert code == 1234
    assert arrow.get(ts) is not None
    return auth_id


def test_get_code():
    auth_id = test_set_code()
    backend = SQLiteAuthBackend(database_name=TEST_DB)
    code, ts, attempts = backend.get_auth_code(auth_id)
    assert code == 1234
    assert arrow.get(ts) is not None
    assert attempts == 0


def test_delete_auth_code():
    auth_id = test_set_code()
    backend = SQLiteAuthBackend(database_name=TEST_DB)
    backend.delete_auth_code(auth_id)
    cur = backend.db_conn.cursor()
    res = get_auth_data(cur, auth_id)
    assert res is None


def test_set_attemtps():
    auth_id = test_set_code()
    backend = SQLiteAuthBackend(database_name=TEST_DB)
    cur = backend.db_conn.cursor()
    code, ts, attempts = get_auth_data(cur, auth_id)
    assert attempts == 0
    backend.set_num_attempts(auth_id, 3)
    cur = backend.db_conn.cursor()
    code, ts, attempts = get_auth_data(cur, auth_id)
    assert attempts == 3
