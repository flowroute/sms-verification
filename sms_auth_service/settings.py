import os


DEBUG_MODE = False

LOG_LEVEL = int(os.environ.get('LOG_LEVEL', 20))
SQLALCHEMY_TRACK_MODIFICATIONS = False

TEST_DB = "test_auth.db"
DB = "auth_codes.db"

FLOWROUTE_ACCESS_KEY = os.environ.get('FLOWROUTE_ACCESS_KEY', None)
FLOWROUTE_SECRET_KEY = os.environ.get('FLOWROUTE_SECRET_KEY', None)
FLOWROUTE_NUMBER = os.environ.get('FLOWROUTE_NUMBER', None)

CODE_LENGTH = int(os.environ.get('CODE_LENGTH', 4))
CODE_EXPIRATION = int(os.environ.get('CODE_EXPIRATION', 3600))  # 1 Hour expiration
RETRIES_ALLOWED = int(os.environ.get('RETRIES_ALLOWED', 3))


ORG_NAME = os.environ.get('ORG_NAME', "Flowroute")
AUTH_MESSAGE = ("{{}}\n"  # Placeholder for authorization code.
                "Welcome to {}! Use this one-time code to "
                "complete your signup.").format(ORG_NAME)
