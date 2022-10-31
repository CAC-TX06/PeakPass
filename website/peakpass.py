import base64
import sqlite3
import hashlib
from flask_login import current_user, login_user, login_required, logout_user
from flask import redirect, render_template, request, url_for
from func.login import correct_login_information
from func.sign_up import add_user, hash_new_pass
from __init__ import create_website
from __init__ import User
import psycopg2
import bcrypt
from reader import CONNECTION_STRING
from cryptography.fernet import Fernet
import hashlib

# Create the actual flask app (imported from __init__.py)
app = create_website()

user_keys = {} # "email": "password"

# Create the default app route
@app.route('/')
def index():
    return render_template('index.html')


# Create the incompatible_width route
@app.route('/incompatible_width')
def incompatible_width():
    return render_template('incompatible_width.html')


# Create the login app route
@app.route('/login', methods = ['POST', 'GET'])
async def login():
    # If the user attempts to login, check the email/username and password against the valid DB entries
    # If the login information is correct, redirect to the dashboard page, otherwise alert the user
    if(request.method == 'POST'):
        if(await correct_login_information(request.form['email'], request.form['password'])):
            user = User()
            user.id = request.form['email']
            login_user(user, remember=True)

            # Hash the password in sha512, turn it into a bytes object, and then encode it in base64
            hashed_pass = hashlib.sha512(request.form['password'].encode()).hexdigest()
            hashed_pass = bytes(hashed_pass[:32], 'utf-8')
            hashed_pass = base64.b64encode(hashed_pass)
            user_keys[user.id] = hashed_pass

            return redirect(url_for('dashboard'))

        return render_template('login.html', error_message='Incorrect email/password. Please try again.')

    elif(request.method == 'GET'):
        if(current_user.is_authenticated):
            return redirect(url_for('dashboard'))

        return render_template('login.html')


# Create the signup route
# If the user attempts to sign up, try to add the new information to the DB, if it fails, then the 
# email/username is already taken, so alert the user, otherwise, redirect to the login page

# Make sure that the passwords are hashed and never stored as plaintext in the DB
@app.route('/signup', methods = ['POST', 'GET'])
async def signup():
    if(request.method == 'POST'):
        response = await add_user(request.form['email'], request.form['password'])
        print(response)
        if response == True:
            return render_template('login.html', success_message='Account created successfully. Please login to continue.')
        elif response == "Email too long":
            return render_template('signup.html', error_message='Email too long. Email addresses must be less than 100 characters. Please try again.')
        elif response == "Password too long":
            return render_template('signup.html', error_message='Password too long. Passwords must be less than 100 characters. Please try again.')
        else:
            return render_template('signup.html', error_message='Email already taken, please try again with a different email address.')

    return render_template('signup.html')


user_pfp_path = {'a':'pfp_a.png', 'b':'pfp_b.png', 'c':'pfp_c.png', 'd':'pfp_d.png', 'e':'pfp_e.png', 
'f':'pfp_f.png', 'g':'pfp_g.png', 'h':'pfp_h.png', 'i':'pfp_i.png', 'j':'pfp_j.png', 'k':'pfp_k.png', 
'l':'pfp_l.png', 'm':'pfp_m.png', 'n':'pfp_n.png', 'o':'pfp_o.png', 'p':'pfp_p.png', 'q':'pfp_q.png', 
'r':'pfp_r.png', 's':'pfp_s.png', 't':'pfp_t.png', 'u':'pfp_u.png', 'v':'pfp_v.png', 'w':'pfp_w.png', 
'x':'pfp_x.png', 'y':'pfp_y.png', 'z':'pfp_z.png'}

# If there is a current user, redirect to the dashboard, otherwise redirect to the login page
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user:
        try:
            path = user_pfp_path[current_user.id[0].lower()]
        except KeyError:
            path = 'pfp_question.png'
        path = url_for('static', filename=path)

        # Get all of the password data
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()
        cur.execute("SELECT id, owner, name, username, password, url FROM passwords WHERE owner = %s", (current_user.id,))
        data = cur.fetchall()
        conn.close()

        data_list = []

        # Create the fernet object for decrypting the passwords, load the key from the user_keys dict as a byte string
        fernet = Fernet(user_keys[current_user.id])
        for i in data:
            i = list(i)

            # Decrypt everything
            name = fernet.decrypt(i[2].encode()).decode('utf-8')
            username = fernet.decrypt(i[3].encode()).decode('utf-8')
            password = fernet.decrypt(i[4].encode()).decode('utf-8')
            url = fernet.decrypt(i[5].encode()).decode('utf-8')

            try:
                img_path = user_pfp_path[name[0].lower()]
            except KeyError:
                img_path = 'pfp_question.png'
            img_path = url_for('static', filename=img_path)

            data_list.append({'owner':current_user.id, 'img':img_path, 'name':name, 'username':username, 'password':password, 'url':url, 'id':i[0]})

        data = sorted(data_list, key=lambda k: k['name'].lower())

        return render_template('dashboard.html', path=path, data=data)


# Create the blog route
@app.route('/blog', methods=['GET'])
def blog():
    return render_template('blog/blog.html')


# Create the blog post route
@app.route('/blog/<post>', methods=['GET'])
def blog_post(post):
    return render_template('blog/' + post + '.html')


# Create the documentation route
@app.route('/documentation', methods=['GET'])
def documentation():
    return render_template('documentation.html')


@app.route('/tools', methods=['GET'])
@login_required
def tools(breached=False):
    if current_user:
        try:
            path = user_pfp_path[current_user.id[0].lower()]
        except KeyError:
            path = 'pfp_question.png'
        path = url_for('static', filename=path)

        return render_template('tools.html', path=path, breached=breached)

    else:
        return render_template('login.html')


@app.route('/account-settings', methods=['GET'])
@login_required
def account_settings():
    if current_user:
        try:
            path = user_pfp_path[current_user.id[0].lower()]
        except KeyError:
            path = 'pfp_question.png'
        path = url_for('static', filename=path)

        return render_template('settings.html', email=current_user.id, path=path)

    else:
        return render_template('login.html')


# Create the route for deleting an account
@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    if current_user:
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()
        cur.execute("SELECT id FROM passwords WHERE owner = %s", (current_user.id,))
        data = cur.fetchall()

        for i in data:            
            cur.execute("DELETE FROM passwords WHERE id = %s", (i[0],))

        # Delete the user from the database
        cur.execute("DELETE FROM users WHERE email = %s", (current_user.id,))

        conn.commit()
        conn.close()

        # Delete the user from the user_keys dict
        del user_keys[current_user.id]

        # Delete the user from the session
        logout_user()

        return redirect(url_for('index'))
    else:
        return render_template('login.html')
        

# Add items to the database (from the 'Add Item' button on the dashboard)
@app.route('/add-item', methods=['POST'])
@login_required
def add_item():
    if current_user:
        # Get the data from the form
        name_form = request.form['name-save']
        username_form = request.form['username-save']
        password_form = request.form['password-save']
        url_form = request.form['url-save']

        # Encrypt it
        fernet = Fernet(user_keys[current_user.id])
        name = fernet.encrypt(name_form.encode()).decode()
        username = fernet.encrypt(username_form.encode()).decode()
        password = fernet.encrypt(password_form.encode()).decode()
        hash = hashlib.sha512(request.form['password-save'].encode()).hexdigest()
        hash = fernet.encrypt(hash.encode()).decode()
        url = fernet.encrypt(url_form.encode()).decode()

        # Add the data to the database
        try:
            conn = psycopg2.connect(CONNECTION_STRING)
            cur = conn.cursor()

            cur.execute("INSERT INTO passwords (owner, name, username, password, hash, url) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, name, username, password, hash, url))
            conn.commit()
            conn.close()
        except:
            pass

        return redirect(url_for('dashboard'))


# Add the delete-item route as a DELETE request with the URL parameters passed from the dashboard delete button
@app.route('/delete-item', methods=['DELETE'])
@login_required
def delete_item():
    if current_user:
        # Get the data from the form
        id = request.args.get('id')
        user = request.args.get('user')

        if current_user.id == user:
            conn = psycopg2.connect(CONNECTION_STRING)
            cur = conn.cursor()

            cur.execute("DELETE FROM passwords WHERE id = %s", (id,))
            conn.commit()
            conn.close()
    
    return render_template('dashboard.html')


# Update an item already in the database
@app.route('/update-item', methods=['POST'])
@login_required
def update_item():
    if current_user:
        # Get the data from the form
        id = request.form['id']
        name = request.form['name-update']
        username = request.form['username-update']
        password = request.form['password-update']
        url = request.form['url-update']

        # Encrypt the data
        fernet = Fernet(user_keys[current_user.id])
        name = fernet.encrypt(name.encode()).decode()
        username = fernet.encrypt(username.encode()).decode()
        password = fernet.encrypt(password.encode()).decode()
        hash = hashlib.sha512(request.form['password-update'].encode()).hexdigest()
        hash = fernet.encrypt(hash.encode()).decode()
        url = fernet.encrypt(url.encode()).decode()

        # Update the data in the database
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()

        try:
            cur.execute("UPDATE passwords SET name = %s, username = %s, password = %s, hash = %s, url = %s WHERE id = %s AND owner = %s", (name, username, password, hash, url, id, current_user.id))
            conn.commit()
            conn.close()
        except:
            pass

        return redirect(url_for('dashboard'))


# Update the users email address
@app.route('/update-email', methods=['POST'])
@login_required
def update_email():
    if current_user:
        # Get the data from the form
        email = request.form['new-email-update']

        # Update the data in the database
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()

        try:
            cur.execute("UPDATE users SET email = %s WHERE email = %s", (email, current_user.id))
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            path = user_pfp_path[current_user.id[0].lower()]
            path = url_for('static', filename=path)
            conn.close()
            return render_template('settings.html', path=path, email=current_user.id, email_error='Email already taken, please try again with a different email address.')

        all_passwords = cur.execute("SELECT * FROM passwords WHERE owner = %s", (current_user.id,))
        all_passwords = cur.fetchall()
        for password in all_passwords:
            cur.execute("UPDATE passwords SET owner = %s WHERE id = %s", (email, password[0]))
        conn.commit()
        conn.close()

        return redirect(url_for('account_settings'))


# Update the users password
@app.route('/update-password', methods=['POST'])
@login_required
def update_password():
    if current_user:
        # Get the data from the form
        cur_pass = request.form['cur-password-update']
        new_pass = request.form['new-password-update']

        if cur_pass == new_pass:
            try:
                path = user_pfp_path[current_user.id[0].lower()]
            except KeyError:
                path = 'pfp_question.png'
            path = url_for('static', filename=path)
            return render_template('settings.html', path=path, email=current_user.id, pass_error='New password cannot be the same as your current password, please try again.')

        # Update the data in the database
        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()

        # Get the users current password from the DB
        cur.execute("SELECT password FROM users WHERE email = %s", (current_user.id,))
        data = cur.fetchone()
        current_password = data[0]

        # Make sure the cur_pass and current_password match using the bcrpyt.checkpw function
        if bcrypt.checkpw(cur_pass.encode('utf-8'), current_password.encode('utf-8')):
            try:
                password = hash_new_pass(new_pass)
                cur.execute("UPDATE users SET password = %s WHERE email = %s", (password, current_user.id))
                conn.commit()
                conn.close()
            except:
                try:
                    path = user_pfp_path[current_user.id[0].lower()]
                except KeyError:
                    path = 'pfp_question.png'
                path = url_for('static', filename=path)
                return render_template('settings.html', path=path, email=current_user.id, pass_error='An error occured, please try again later.')
        else:
            try:
                path = user_pfp_path[current_user.id[0].lower()]
            except KeyError:
                path = 'pfp_question.png'
            path = url_for('static', filename=path)
            return render_template('settings.html', path=path, email=current_user.id, pass_error='The password you entered was not your current password. Please try again.')

        return redirect(url_for('account_settings'))


# Create the password breach check route
@app.route('/check-passwords', methods=['POST'])
@login_required
def check_passwords():
    if current_user:
        # Get all of the users passwords from the database

        conn = psycopg2.connect(CONNECTION_STRING)
        cur = conn.cursor()
        cur.execute("SELECT hash FROM passwords WHERE owner = %s", (current_user.id,))
        data = cur.fetchall()

        breach_conn = sqlite3.connect('breached_passwords.db')
        breach_cur = breach_conn.cursor()

        # Create a list of all of the users passwords
        breached = []
        fernet = Fernet(user_keys[current_user.id])
        for password in data:
            decrypted_password = fernet.decrypt(str(password).encode()).decode()

            # See if the password is in the breached_passwords database
            breach_cur.execute("SELECT * FROM breached_passwords WHERE password = ?", (decrypted_password,))
            data = breach_cur.fetchone()

            # If the password is in the breached_passwords database, add it to the list
            if data:
                cur.execute("SELECT name FROM passwords WHERE hash = %s", (password,))
                name = cur.fetchone()
                name = fernet.decrypt(str(name).encode()).decode()
                breached.append(f'"{name}"')

        conn.close()
        breach_conn.close()

        # Load the tools route and pass the breached passwords list to it
        try:
            path = user_pfp_path[current_user.id[0].lower()]
        except KeyError:
            path = 'pfp_question.png'
        path = url_for('static', filename=path)

        return render_template('tools.html', path=path, breached=breached)


# Logout the user and redirect to the index page
@app.route('/logout', methods=['GET'])
def logout():
    if current_user:
        logout_user()

    return redirect(url_for('index'))


# If there is a 404 error, then render the 404.html page, for 505 errors, render the index page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))

@app.errorhandler(405)
def method_not_allowed(e):
    return redirect(url_for('index'))

@app.errorhandler(500)
def error_500(e):
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Run on localhost at port 5000
    app.run(host='localhost', port=5000)