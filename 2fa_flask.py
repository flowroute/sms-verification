from random import randint
from flask import Flask, render_template, request
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, validators

from FlowrouteMessagingLib.Controllers.APIController import APIController
from FlowrouteMessagingLib.Models import Message


app = Flask(__name__)
app.debug = True
app.secret_key = 'Your_app_secret_key'

controller = APIController(username="AccessKey", password="SecretKey")


class UserForm(Form):
    """
    Validates user input to ensure the phone number is of proper length.
    Exposes a TextField where the user can submit the secret code.
    """
    toNumber = TextField(
        "Phone Number",
        [validators.required("Please enter your cell phone number"),
            validators.Length(min=11, max=11)])
    submit = SubmitField("Send Confirmation Code")
    pinField = TextField("Secret Code")
    checkPin = SubmitField("Validate your pin")


@app.route("/", methods=['GET', 'POST'])
def user_verification():
    """
    Renders the 2 factor authentication form, generates a secret code, 
    and verifies they are equal on submission.
    """
    global SECRET_CODE
    form = UserForm()
    if request.method == 'GET':
        return render_template('index.html', form=form)
    elif request.method == 'POST':
        if form.validate() is False:
            return render_template('index.html', form=form)
        elif 'submit' in request.form:
            SECRET_CODE = str(randint(999, 9999))
            recipient = str(form.toNumber.data)
            msg = Message(
                to=recipient,
                from_="18444205780",
                content=SECRET_CODE)
            controller.create_message(msg)
            return render_template('index.html', form=form)
        elif str(form.pinField.data) == SECRET_CODE:
            return "Pin validated successfully"
        else:
            return "Pin validation failed"

if __name__ == "__main__":
    app.run()
