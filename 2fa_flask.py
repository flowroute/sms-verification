from flask import Flask, render_template, request, flash
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, validators, ValidationError
from FlowrouteMessagingLib.Controllers.APIController import *
from FlowrouteMessagingLib.Models import * 
from random import randint

controller = APIController(username="AccessKey", password="SecretKey")       

app = Flask(__name__)
app.debug = True
app.secret_key = 'Your_app_secret_key'

@app.route("/", methods=['GET', 'POST'])
def main():

  global secretCode

  class UserForm(Form):
    toNumber = TextField("Phone Number", [validators.required("Please enter your cell phone number"), validators.Length(min=11, max=11)])
    submit = SubmitField("Send Confirmation Code")
    pinField = TextField("Secret Code")
    checkPin = SubmitField("Validate your pin")
  
  form = UserForm() 

  if request.method == 'GET':
    return render_template('index.html', form=form)

  elif request.method == 'POST':
    if form.validate() == False:
          return render_template('index.html', form=form)
    elif 'submit' in request.form:  
      secretCode = str(randint(999,9999))
      recipient = str(form.toNumber.data)
      msg = Message(to=recipient, from_="18444205780", content=secretCode)
      response = controller.create_message(msg)
      return render_template('index.html', form=form)         
    else:
      if str(form.pinField.data) == secretCode:
        return "Pin validated successfully"
      else:
        return "Pin validation failed"

if __name__ == "__main__":
  app.run()
