An SMS authorization micro-service

The project contains a Flask app serving up a single resource at the site base.
The service uses a SQLite backend
A credential.py file is required at the application level with the following values (accessable via Flowroute Manager)

FLOWROUTE_ACCESS_KEY = 'your_tech_prefix'
FLOWROUTE_SECRET_KEY = 'your_api_secret_key'
FLOWROUTE_NUMBER = 'your_flowroute_number'

-There is a code generation function whose length is configurable from settings.py
-The number of authorization tries allowed, and the code expiration is also 
    configurable from settings.py
-The company name that appears in the SMS content can be set via settings.py

During development DEBUG_MODE should be left True to maintain the production db

To run using docker, the service can be built with 'docker build -t sms_auth_api .' at the top level of the project, then 'docker run -p 8000:8000 sms_auth_api' (starts 4 gunicorn workers listening on the docker-machine port 8000) - defined in the 'entry' script.


To run locally with Flask's built in development web server, simply use 'python -m sms_auth_service.api'
