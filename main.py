from flask import Flask
from flask import redirect, render_template, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import json
import secrets
import os

# Initialize the Flask application
app = Flask(__name__)

# Load configuration parameters from a JSON file
with open('config.json', 'r') as c:
    params = json.load(c)['params']

# Set database URI based on the server type
LOCAL_SERVER = params['local_server']
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] if LOCAL_SERVER else params['production_uri']

# Set a secret key for session management securely
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))

# Initialize the database
db = SQLAlchemy(app)

# Database Model for Contacts
class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    message = db.Column(db.String(100), nullable=False)

# Contact Form Model using Flask-WTF
class ContactForm(FlaskForm):
    name = StringField('Name', [Length(min=4, max=25)])
    email = StringField('Email Address', [DataRequired(), Email(granular_message=True)])
    message = StringField('Message', [DataRequired()])
    submit = SubmitField('Send')


""" <-----------------------------Route for the contact form -----------------------------> """

@app.route("/", methods=["GET", "POST"]) 
def contact():
    # Instantiate the contact form
    rform = ContactForm()

    # Handle form submission
    if request.method == 'POST' and rform.validate_on_submit():
        # Get form data
        name = rform.name.data
        email = rform.email.data
        message = rform.message.data

        # Create a new contact entry and save it to the database
        contact_entry = Contacts(name=name, email=email, message=message)
        db.session.add(contact_entry)
        db.session.commit()

        # Flash success message
        flash('Message sent successfully!', 'success')
        return render_template("contact.html", form=rform)
    
    # Flash error message for invalid input
    flash('Invalid input, try again please', 'error')
    return render_template("contact.html", form=rform)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
