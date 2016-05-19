# SMS Identity Authorization

SMS Identity Authorization is a microservice that allows you to add an extra layer of security to your application; with this service you can generate an authorization code, and then send that code by SMS to a specified recipient. The recipient must then respond with that code to to allow access to that application. For example, the recipient might need to respond with the code on a web page to access that site. You can also customize the code length, allotted time to respond, and the number of permitted retries before disallowing access. 

The service uses a SQLite backend and exposes an API endpoint which generates and validates verification requests using two methods: **POST** and **GET**.

* **POST** generates the authorization code, which includes a customizable expiration date, code length, number of retries, and custom message before dispatching an SMS to the specified recipient.

* **GET** validates the request data; after running verification on the returned authorization code, either returns a response success or an error message.

## Before you deploy SMS Identity Authorization

You will need your Access Key, Secret Key, and your SMS-enabled Flowroute number. If you do not know your Flowroute information:

* Your Access Key and Secret Key can be found on the <a href="https://manage.flowroute.com/accounts/preferences/api/" target="_blank">API Control</a> page on the Flowroute portal.
* Your Flowroute phone numbers can be found on the <a href="https://manage.flowroute.com/accounts/dids/" target="_blank">DIDs</a> page on the Flowroute portal.


##Run `git clone` and create a credentials.py file

1.	If needed, create a parent directory where you want to deploy SMS Identify Authorization.

2.	Change to the parent directory, and run the following:

		git clone https://github.com/flowroute/sms-verification.git

	The `git clone` command clones the **sms-verification** repository as a sub directory within the parent folder.

4.	Create a **credentials.py** file that includes your Flowroute credentials. 
	This is done to help protect against committing private information to a remote repository. 

	* Using a code text editor — for example, **Sublime Text** — add the following lines to a new file, replacing the Access Key, Secret Key, and your Flowroute phone number with the information from your Flowroute account.

			FLOWROUTE_ACCESS_KEY = "Your Access Key"
			FLOWROUTE_SECRET_KEY = "Your Secret Key"
			FLOWROUTE_NUMBER = "Your 11-digit, 1XXXXXXXXXX-formatted Flowroute phone number."

	*	Save the file as **credentials.py** in the **sms\_auth_service directory**.

7.	Deploy the service.

## Deploy SMS Identify Authorization

Deploying the service can be done by either building and running a Docker container as specified by the provided **Dockerfile**, or by running the application locally with Flask's built-in web server. You can first run the application in test mode before running in production mode. 

>**Note:** During development DEBUG\_MODE should be set to `True` to use the auto-generated test database. Testing can be performed on this database, which drops data in the tables each time the test module is run. Once the development cycle is over, set DEBUG\_MODE to `False` in order to use the production database. Tests cannot be run when the production database is active.

##### To run the application using Docker:	

1.	Run the following at the project's top level to build the service:

		$ docker build -t sms_auth_api:0.0.1 .

	`-t` tags the image, allowing you to reference it by name instead of by image ID.

2. Next, run the following:

		$ docker run -p 8000:8000 sms_auth_api:0.0.1

	`-p` binds the container port to the Docker host port. When using a virtualization layer, such as Docker-machine, the API should now be exposed on that host — for example, `http://192.168.99.100:8000`.

	By default, the `run` command spawns four Gunicorn workers listening on port `8000`. To modify the `run` command, edit the settings in the Docker **entry** file located in the project root.

##### To run the application locally:

1.	From your **sms_verification **directory, run:

		pip install -r requirements.txt

2.	Run the following to install the service dependencies at the root level of the project:

		pip install .
		
3.	Finally, run:

		python -m sms_auth_service.api

	The service is set up at the root level.

>**Note:** See the <a href="http://flask.pocoo.org/" target="_blank">Flask</a> documentation for more information about the web framework.


## Configure SMS Identity Authorization

With the service now deployed, configure authorization settings by either customizing and running **settings.py** or by running **client.py**.

### settings.py

**settings.py** allows you to customize the authorization code, including the code length, expiration time, number of retries, company name, and message. 

##### To configure the authorization settings:

1. In the **sms\_auth_service** directory, open **settings.py**.

2. Modify any of the following values as needed:

		CODE_LENGTH = 4
		CODE_EXPIRATION = 3600  # 1 Hour expiration
		RETRIES_ALLOWED = 3
		ORG_NAME="Your Organization Name"
		AUTH_MESSAGE=("{{}}\n"  # Placeholder for authorization code.
                "Welcome to {}! Use this one-time code to "
                "complete your signup.").format(ORG_NAME)

	###### settings.py parameters

	| Variable |  Data type   |Constraint                                                                                	|
	|-----------|----------|----------|------------------------------|
	|`CODE_LENGTH`| INT	   | Sets the length of the generated authorization code. There is neither a minimum nor maximum number of allowed digits. The default length is `4` (four) digits.| 
	|`CODE_EXPIRATION`| INT| The length of time, in seconds and including retries, before the authorization code expires. There is no limit on the time. The default value is `3600` seconds (one hour).
	|`RETRIES_ALLOWED`|INT|	The number of retries allowed before the code is invalid. There is no limit on the number of retries you can set. The default retry is `3` times. |
	|`ORG_NAME`|String|The name you to display in the authorization message within the enclosing quotes (`""`). Alphanumeric characters are supported. There are no disallowed characters, and there is no limit on the number of characters. The default name is `Your Organization Name`.|
	|`AUTH_MESSAGE`|String|The message sent with the code. There is no limit on the number of alphanumeric characters that can be used, and there are no disallowed characters. If the message exceeds 160 characters, however, it will be broken up into multiple messages. See <a href="https://developer.flowroute.com/docs/message-length-concatenation" target="_blank">Message Length & Concatenation</a> for more information on message length.|

3. Save the file.

### client.py

The SMSAuthClient can be imported from **client.py** and instantiated with the `SMS_AUTH_ENDPOINT` as it's only argument. The SMSAuthClient has two methods, `create_auth` and `authenticate_code`, which proxy to the service resource endpoints.  

**client.py** reads the response and returns a success or error message as needed.

The module is located within the **sms\_auth_service** Python package.

## Test it! 
	
In a test environment, invoke the `docker run` command with the `test` argument to run tests and see results. To change the `docker run` command options, modify the `test`, `coverage`, or `serve` options in the `entry` script located in the top level **sms-verification** directory. 

>**Note:** To learn more about Docker entry points, see <a href="https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/" target="_blank"> Dockerfile Best Practices</a>.

*	Run the following:

		$ docker run -p 8000:8000 sms_auth_api:0.0.1 test

	A `py.test` command is invoked from within the container. When running `coverage`, a cov-report directory is created that contains an **index.html** file detailing test coverage results.

## Send and validate an authorization code

Once the application is up-and-running, the authorization resources can now be invoked with their respective request types.

### Send the code (POST)

Generate and send the code. You can:

* use a curl **POST** command:

		curl -v -X POST -d '{"auth_id": "my_identifier", "recipient": "my_phone_number"}' -H "Content-Type: application/json" localhost:8000

	| Key: Argument | Required | Constraint |
	|-----------|----------|---------------------------------------------------------------|
|`auth_id: Identifier`|Yes|The `my_identifier` is any user-defined string, limited to 120 characters. For example, this could be a UUID.
|`recipient: my_phone number`|Yes|`my_phone_number` is the phone number identifying the recipient using an 11-digit, number formatted as *1XXXXXXXXXX*. Validation is performed to ensure the phone number meets the formatting requirement, but no validation is performed to determine whether or not the phone number itself is valid. |

	>**Important:** When using the **POST** method with JSON you must also include the complete `Content-Type:application/json" localhost:8000` header.

* use the client class stored in **client.py**: 

		from client import SMSAuthClient 
		my_client = SMSAuthClient(endpoint="localhost:8000")
		my_client.create_auth("my_identifier", "my_phone_number")

A code is auto-generated based on the modifications made to **settings.py** and sent to the intended recipient. The recipient then receives the message and code at the number passed in the POST method.

### Validate the authorization code (GET)

* Run the following:

		url -X GET "http://localhost:8000?auth_id=my_identifier&code=1234"

	In this example,
	*	`my_identifier` is the `auth_id` from the **POST** request.

	* 	`1234` is the value passed through from user input.

	>**Important!** URL encoding is required for the **GET** request.
				
The following then occurs:

1.	The `auth_id` is validated. If the authorization ID is not recognized, a **400** status code is returned.

2. 	The code is checked against the expiration time. If the code has expired, the entry is deleted, and no attempts for that `auth_id` will be recognized. A **400** status code is returned.

3. 	If the code has not expired, but the attempt does not match the stored code, retries based on the `RETRIES_ALLOWED` number set in **settings.py** begin.
	* If the code matches the stored code, a **200** success message is returned, and the entry is removed from the database.
	* If the number of retries is reached without success, no more retries are allowed, and the entry is removed from the database.

	>**Note:** Because they are no longer needed, validated and failed authorization entries are removed  in order to keep database size down.

#### Success response

A valid authorization code returns a **200** status code and success message.

#### Error response

The following describe the possible error status codes:

*  a **400** status code for invalid attempts, if the code has expired, or if the `auth_id` is not recognized. The number of retry attempts remaining is stored in the response data, along with the reason for the failure and the exception type.
*  a **500** status code for an internal error, or if a phone number is not reachable on the network.


## Contributing
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
