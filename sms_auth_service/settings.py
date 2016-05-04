import os


DEBUG_MODE = True
LOG_LEVEL = int(os.environ.get('LOG_LEVEL', 20))
SQLALCHEMY_TRACK_MODIFICATIONS = False

TEST_DB = "test_auth.db"
DB = "auth_codes.db"

CODE_LENGTH = 4
CODE_EXPIRATION = 3600  # 1 Hour expiration
RETRIES_ALLOWED = 3

COMPANY_NAME = 'Flowroute'
