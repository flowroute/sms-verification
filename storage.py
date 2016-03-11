import sqlite3 as sqlite
import boto3

from settings import CODE_LENGTH


class InternalStorageError(Exception):
    pass


class CodeNotSetError(InternalStorageError):
    pass


class UserNotFoundError(InternalStorageError):
    pass


class TwoFactorAuthStorageBackend(object):

    def set_user_code(self, user_id, code):
        raise NotImplementedError

    def get_user_code(self, user_id):
        raise NotImplementedError

    def remove_code(self, user_id):
        raise NotImplementedError

    def remove_user(self, user_id):
        raise NotImplementedError


class SQLiteStorageBackend(TwoFactorAuthStorageBackend):

    def __init__(self, database_name='authorization.db'):
        self.db_conn = sqlite.connect(database_name)
        inst_table_q = ("CREATE TABLE IF NOT EXISTS user_codes"
                        "(user_id TEXT PRIMARY KEY, code INTEGER,"
                        "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        with self.db_conn:
            self.db_conn.execute(inst_table_q)

    def set_user_code(self, user_id, code):
        assert len(str(code)) == CODE_LENGTH
        with self.db_conn:
            self.db_conn.execute(
                ("INSERT OR REPLACE INTO "
                 "user_codes(user_id, code) VALUES (?, ?)"),
                (user_id, code))

    def get_user_code(self, user_id):
        cur = self.db_conn.cursor()
        cur.execute(
            "SELECT code, timestamp FROM user_codes WHERE user_id = ?",
            (user_id,))
        result = cur.fetchone()
        if result is None:
            raise CodeNotSetError(
                "Unable to find a code set for customer {}".format(user_id))
        else:
            return result

    def remove_code(self, user_id):
        with self.db_conn:
            self.db_conn.execute(
                ("UPDATE user_codes SET code = ?, timestamp = ?"
                 "WHERE user_id = ?"),
                (None, None, user_id))

    def remove_user(self, user_id):
        with self.db_conn:
            self.db_conn.execute(
                "DELETE FROM user_codes WHERE user_id = ?",
                (user_id,))
