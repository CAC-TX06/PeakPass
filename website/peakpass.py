from flask_login import current_user, login_user, login_required, logout_user
from flask import redirect, render_template, request, url_for, flash
import sqlalchemy
from func.login import correct_login_information
from func.sign_up import add_user, hash_new_pass
from __init__ import create_website
from __init__ import User
import psycopg2
from reader import USER, PASSWORD, DATABASE, HOST

# Create the actual flask app (imported from __init__.py)
app = create_website()

# Create the default app route
@app.route('/')
def index():
    return render_template('index.html')

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
        if await add_user(request.form['email'], await hash_new_pass(request.form['password'])):
            # redirect(url_for('login'))
            return render_template('login.html', success_message='Account created successfully. Please login to continue.')
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
        path = user_pfp_path[current_user.id[0].lower()]
        path = url_for('static', filename=path)

        # Get all of the password data
        conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
        cur = conn.cursor()
        cur.execute("SELECT owner, name, username, password, url, id FROM passwords WHERE owner = %s", (current_user.id,))
        data = cur.fetchall()
        conn.close()

        data_list = []

        for i in data:
            i = list(i)
            img_path = user_pfp_path[i[1][0].lower()]
            img_path = url_for('static', filename=img_path)

            data_list.append({'img':img_path, 'name':i[1], 'username':i[2], 'password':i[3], 'url':i[4], 'id':i[5]})

        print(data_list)

        return render_template('dashboard.html', path=path, data=data_list)
        
    return redirect(url_for('login'))


#Add items to the database (from the 'Add Item' button on the dashboard)
@app.route('/add-item', methods=['POST'])
@login_required
def add_item():
    if current_user:
        # Get the data from the form
        name = request.form['name-save']
        username = request.form['username-save']
        password = request.form['password-save']
        url = request.form['url-save']

        # Add the data to the database
        try:
            conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
            cur = conn.cursor()

            cur.execute("INSERT INTO passwords (owner, name, username, password, url) VALUES (%s, %s, %s, %s, %s)", (current_user.id, name, username, password, url))
            conn.commit()
            conn.close()

        except sqlalchemy.exc.IntegrityError:
            print("Error: Duplicate ID")  

        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login'))
    

#Update an item already in the database
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

        # Update the data in the database
        conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
        cur = conn.cursor()

        cur.execute("UPDATE passwords SET name = %s, username = %s, password = %s, url = %s WHERE id = %s AND owner = %s", (name, username, password, url, id, current_user.id))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login'))


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

@app.errorhandler(500)
def error_500(e):
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Run on localhost at port 5000
    app.run(host='localhost', port=5000)