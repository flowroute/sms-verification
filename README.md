# SMS authorization micro-service

## General Information
The project contains a Flask app serving up a single resource at the site base.
The service uses a SQLite backend.
A credential.py file is required at the application level with the following values (accessable via Flowroute Manager)

FLOWROUTE_ACCESS_KEY = 'your_tech_prefix'

FLOWROUTE_SECRET_KEY = 'your_api_secret_key'

FLOWROUTE_NUMBER = 'your_flowroute_number'

## Installation and Serving the App
-There is a code generation function whose length is configurable from settings.py
-The number of authorization tries allowed, and the code expiration is also 
    configurable from settings.py
-The company name that appears in the SMS content can be set via settings.py

During development DEBUG_MODE should be left True to maintain the production db

To run using docker, the service can be built with 'docker build -t sms_auth_api .' at the top level of the project, then 'docker run -p 8000:8000 sms_auth_api' (starts 4 gunicorn workers listening on the docker-machine port 8000) - defined in the 'entry' script.


To run locally with Flask's built in development web server, simply use 'python -m sms_auth_service.api'. First install the service dependencies with 'pip install .' at the root level of the project.

## Using the Service
The service can create/send a new code by either using the client class stored in 'client.py' or using a curl command like:
curl -v -X POST -d '{"auth_id": "my_session_id", "recipient": "phone_number"}' -H "Content-Type: application/json" localhost:8000

To validate the code:
url -X GET "http://localhost:8000?auth_id=my_session_id&code=2766"

The service will respond with a 400 status code for invalid attempts, aif the code has expired, or if the auth_id is not recognized. The number of attempts remaining is stored in the response data, along with the reason for failure, and exception type.

If the code is valid the service will respond with a 200 status code, and success message.
