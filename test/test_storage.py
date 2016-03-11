import pytest
import sqlite3 as sqlite
import uuid
import arrow

from ..storage import SQLiteStorageBackend

TEST_DB = 'test_authorization.db'


@pytest.fixture
def fresh_table():
    conn = sqlite.connect(TEST_DB)
    with conn:
        conn.execute('DROP TABLE IF EXISTS user_codes')
    return conn


def test_create_table(fresh_table):
    backend = SQLiteStorageBackend(database_name=TEST_DB)
    cur = backend.db_conn.cursor()
    cur.execute("PRAGMA table_info([user_codes])")
    res = cur.fetchall()
    cur.close()
    assert 'user_id' in res[0] and 'TEXT' in res[0]
    assert 'code' in res[1] and 'INTEGER' in res[1]
    assert 'timestamp' in res[2] and 'DATETIME' in res[2]


def test_set_code():
    new_conn = fresh_table()
    backend = SQLiteStorageBackend(database_name=TEST_DB)
    user_id = str(uuid.uuid1())
    backend.set_user_code(user_id, 1234)
    cur = new_conn.cursor()
    cur.execute(
        "SELECT code, timestamp FROM user_codes WHERE user_id = ?",
        (user_id,))
    res = cur.fetchone()
    cur.close()
    assert res[0] == 1234
    assert arrow.get(res[1]) is not None
    return user_id


def test_get_code():
    user_id = test_set_code()
    backend = SQLiteStorageBackend(database_name=TEST_DB)
    code, ts = backend.get_user_code(user_id)
    assert code == 1234
    assert arrow.get(ts) is not None


def test_remove_code():
    user_id = test_set_code()
    backend = SQLiteStorageBackend(database_name=TEST_DB)
    backend.remove_code(user_id)
    cur = backend.db_conn.cursor()
    cur.execute(
        "SELECT code, timestamp FROM user_codes WHERE user_id = ?",
        (user_id,))
    code, timestamp = cur.fetchone()
    cur.close()
    assert code is None
    assert timestamp is None


def test_remove_user():
    user_id = test_set_code()
    backend = SQLiteStorageBackend(database_name=TEST_DB)
    backend.remove_user(user_id)
    cur = backend.db_conn.cursor()
    cur.execute(
        "SELECT code, timestamp FROM user_codes WHERE user_id = ?",
        (user_id,))
    res = cur.fetchone()
    cur.close()
    assert res is None
