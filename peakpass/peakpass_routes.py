from flask import Flask
from flask import Flask, redirect, render_template, request, session, url_for
from reader import USER, PASSWORD, DATABASE, HOST
import os
import asyncpg
import random
from hashlib import pbkdf2_hmac
import string
from datetime import timedelta
from func.login import correct_login_information
from func.sign_up import add_user, hash_new_pass


# Create the Flask application and a random 32 character secret key as well as the pepper value
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

app.secret_key = os.urandom(32)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

@app.route('/')
def index():
    return render_template('index.html')

# Create the default app route
@app.route('/login', methods = ['POST', 'GET'])
async def login():
    # If the user attempts to login, check the email/username and password against the valid DB entries
    # Make sure that the passwords are hashed and never stored as plaintext in the DB
    try:
        if(request.method == 'POST'):
            if await correct_login_information(request.form['email'], request.form['password']):
                session["email"] = True
                return redirect(url_for('dashboard'))
            else:
                return render_template('login-incorrect.html')

        elif(request.method == 'GET'):
            try:
                if session["email"]:
                    return redirect(url_for('dashboard'))
            except:
                pass
            return render_template('login.html')
    except:
        pass


@app.route('/signup', methods = ['POST', 'GET'])
async def signup():
    # If the user attempts to sign up, check the email/username and password against the valid DB entries
    # Make sure that the passwords are hashed and never stored as plaintext in the DB
    try:
        if(request.method == 'POST'):
            email = request.form['email']
            password = request.form['password']
            info = await hash_new_pass(password)
            if await add_user(email, info):
                return render_template('signup-success.html')
            else:
                return render_template('signup-failure.html')

        elif(request.method == 'GET'):
            return render_template('signup.html')
    except:
        pass


@app.route('/dashboard', methods=['GET'])
def dashboard():
    try:
        if session["email"]:
            return render_template('dashboard.html')
    except:
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    # Try to pop the users session
    try:
        session.pop("email")
    # Otherwise, pass
    except KeyError:
        pass
    # Now, redirect to the main page
    return redirect(url_for('index'))


# If there is a 404 or 500 error, return render the index.html file
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('error_404'))

@app.route('/404', methods=['GET'])
def error_404():
    return render_template('404.html')

@app.errorhandler(500)
def error_500(e):
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Run on localhost at port 5000
    app.run(host='localhost', port=5000)