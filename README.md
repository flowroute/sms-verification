# SMS Authorization Microservice
The SMS Authorization microservice is a service that allows you to create an authorization code and expiration date, and then sent by SMS to a specified recipient. 
## About the Authorization Microservice

The project contains a Flask app serving up a single resource at the site base.
The service uses a SQLite backend.

The authorization code, expiration date, and number of retries are user-defined within **settings.py**.

The microservice uses two methods: POST and GET. POST generates the authorization code, expiration date, code length, and retries. GET then validates the data and either returns a success message or an error exception. 

###Before you install the service

A **credential.py** file is required at the application level that includes your Access Key, Secret Key, and your Flowroute number enabled for SMS. If you do not know this information, you can find them on the [Flowroute](https:https://manage.flowroute.com) portal. 

The following lines should be added to the **credential.py** file:

	FLOWROUTE_ACCESS_KEY = "Your Access Key"

	FLOWROUTE_SECRET_KEY = "Your Secret Key"

	FLOWROUTE_NUMBER = "Your Flowroute phone number"
## Installing the service

The application contains a code-generation function whose length is configurable from **settings.py**. The function can be configured to allow a specific number of retries as well as an expiration date.

The company name that appears in the SMS content can be set via settings.py

>**Note:** During development DEBUG\_MODE should be set to `True` to use a test database. Testing can be performed on this database, which refreshes data in the tables each time. Once the development cycle is over, set DEBUG\_MODE to `FALSE` in order to use the production database. Tests cannot be peformed on the production database.  

Deploying the service can be done either by running the setup using Docker or by running the application locally with Flask's built-in web server

#####To run the application using Docker:	

1.	Run the folowing to build the service at the top level of the project:

		$ docker build -t sms_auth_api:0.0.1 .

-t tags the image allowing you to reference it.

2. Next, run the following:

		$ docker run -p 8000:8000 sms_auth_api:0.0.1
	
	-p binds the container port to the host port. You cannot have multiple applications listening on the same port.
	
###	Test the application 
	
	This starts four gunicorn workers listening on the port 8080 of the Docker system. This information is defined in the `entry` script.

the entry script takes the last command that was passed from the `run` command. Unit testing. Won't run if debug is false.

	$ docker run -p 8000:8000 sms_auth_api:0.0.1 test


#####To run the application using Flask:

1.	Run the following to install the service dependencies at the root level of the project:

		pip install .

2. Next, run the following:
		
		python -m sms_auth_service.api
	
	The service is set up at the root level.
	
>**Note:** See the [Flask](a href="http://flask.pocoo.org/") documentation for more information about the web framework.

##Configure the authorization setings
Authorization settings can be configured using one of two methods: Update the **settings.py** file or use **client.py**.

###settings.py
**settings.py** allows you to customize the authorization parameters, including authorization code length, expiration, number of retries, and company name. 

#####To configure the authorization settings:

1. Open **settings.py**.

2. Modify any of the following lines as needed: 
		
		CODE_LENGTH = 4
		CODE_EXPIRATION = 3600  # 1 Hour expiration
		RETRIES_ALLOWED = 3
		COMPANY_NAME="Flowroute"

	######settings.py parameters

	| Parameter | Required | Data type|Usage                                                                                	|
	|-----------|----------|----------|------------------------------|
	|`CODE_LENGTH`| Yes|	INT	| Sets the length of the authorization code. There is neither no minimum nor maximum number of digits. The default length value is `4` (four) digits long.| 
	|`CODE_EXPIRATION`|Yes| INT| The length of time, in seconds, before the authorization code expires. There is no limit on the time. The default value is `3600` seconds (one hour).
	|`RETRIES_ALLOWED`|Yes	|INT|	The number of retries allowed before the code is invalid. There is no limit on the number of retries. The default value is `3` retries. |
	|`COMPANY_NAME`|Yes|String|The company name variable. There is no limit on the number of alphanumeric characters that can be used. The default name is `Flowroute`.|

3. Save the file.

##client.py
 **client.py** optionally allows you to deploy the microservice using Python to make the request; it also allows you to work the API as an object in memory. **client.py** contains the endpoint and two methods, `create_auth` and `authenticate_code`. 

**client.py** reads the response and raises an HTTP exeption with error code 400 if the status code is a 400 it will raise an http exception. That exception is going to have on it an attribute message and a str error, which maps to the string version of the error. A successful request returns a success response object.

The file is located at **mfa-app/sms\_auth_service**.

## Using the Service

Depending on which method you used to deploy the service, the service can be invoked by running either of the following:

###Send the code

The service can create/send a new code by either of the following:

* using a curl POST command if you set up the service using **settings.py**:

		curl -v -X POST -d '{"auth_id": "my_session_id", "recipient": "phone_number"}' -H 
		 "Content-Type: application/json" localhost:8000
	
	| Parameter | Required | Usage |                                                                               
|-----------|----------|---------------------------------------------------------------|
|`my_session_id`|Yes|Any string identifying the auth_id, limited to 120 characters.
|`phone_number`|Yes|Phone number identifying the recipient using an 11-digit, E.164 formatted *1NPANXXXXXXXXX* number. Validation is performed to ensure the phone number meets the formatting requirement, but validation is performed on whether or not the phone number itself is valid. 

	>**Important:** When using POST method with JSON you must also include the complete `Content-Type:application/json" localhost:8000` header. 

* using the client class stored in **client.py** 

###Validate the code:
* Run the following:

		url -X GET "http://localhost:8000?auth_id=my_session_id&code=2766"
		
>**Important!** URL encoding is required for the GET request.
		
GET request needs the auth id and the code (strings). URL encoding is required, which is why they need to use strings.  

The first thing validated is the auth_id is recognized. 400 for not recognized.
Second, the code is checked for expiration, and is it still valid.
If code is expired, no retries. Also a code 400. Custom exception types. 500 returned for incorrect recipient number or malformtting.
Third, if the code is not equal to stored code; are attempts equal to max attempts. if code equals stored, 200 returned success. If so, there are no attempts remaining, and the code is removed. But success removes the code as well to keep db smaller.

####Success response

A valid code returns a response with a 200 status code and success message.

####Error response

The service will respond with a 400 status code for invalid attempts, if the code has expired, or if the `auth_id` is not recognized. The number of attempts remaining is stored in the response data, along with the reason for failure and exception type.


If the code is valid the service will respond with a 200 status code, and success message.

## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D


