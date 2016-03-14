import sqlite3 as sqlite


class InternalStorageError(Exception):
    pass


class CodeNotSetError(Exception):
    pass


class AuthStorageBackend(object):

    def set_auth_code(self, auth_id, code):
        raise NotImplementedError

    def get_auth_code(self, auth_id):
        raise NotImplementedError

    def set_num_attempts(self, auth_id, attempts_made):
        raise NotImplementedError

    def delete_auth_code(self, auth_id):
        raise NotImplementedError


class SQLiteAuthBackend(AuthStorageBackend):

    def __init__(self, database_name):
        self.db_conn = sqlite.connect(database_name)
        inst_table_q = ("CREATE TABLE IF NOT EXISTS codes"
                        "(auth_id TEXT PRIMARY KEY, code INTEGER, "
                        "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, "
                        "attempts INTEGER DEFAULT 0)")
        with self.db_conn:
            self.db_conn.execute(inst_table_q)

    def set_auth_code(self, auth_id, code):
        try:
            with self.db_conn:
                self.db_conn.execute(
                    ("INSERT OR REPLACE INTO "
                     "codes(auth_id, code) VALUES (?, ?)"),
                    (auth_id, code))
        except sqlite.Error as e:
            raise InternalStorageError(e)

    def get_auth_code(self, auth_id):
        cur = self.db_conn.cursor()
        try:
            cur.execute(
                ("SELECT code, timestamp, attempts FROM codes "
                 "WHERE auth_id = ?"),
                (auth_id,))
        except sqlite.Error as e:
            raise InternalStorageError(e)
        result = cur.fetchone()
        cur.close()
        if result is None:
            raise CodeNotSetError(
                "Unable to find a code set for auth_id {}".format(auth_id))
        else:
            return result

    def delete_auth_code(self, auth_id):
        with self.db_conn:
            try:
                self.db_conn.execute(
                    "DELETE FROM codes WHERE auth_id = ?",
                    (auth_id,))
            except sqlite.Error as e:
                raise InternalStorageError(e)

    def set_num_attempts(self, auth_id, attempts_made):
        with self.db_conn:
            try:
                self.db_conn.execute(
                    ("UPDATE codes SET attempts = ? "
                     "WHERE auth_id = ?"),
                    (attempts_made, auth_id))
            except sqlite.Error as e:
                raise InternalStorageError(e)
