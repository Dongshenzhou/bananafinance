from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, DateField, RadioField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import userDAO, followDAO, portfolioDAO
import myiex
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'banana.cixexwwhho0d.ap-southeast-2.rds.amazonaws.com'
app.config['MYSQL_PORT'] = 8000
app.config['MYSQL_USER'] = 'banana'
app.config['MYSQL_PASSWORD'] = 'banana1234'
app.config['MYSQL_DB'] = 'bananafinance'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_CONNECT_TIMEOUT'] = 100
# init MYSQL
mysql = MySQL(app)



# Index
@app.route('/',methods = ['GET','POST'])
def index():
    form = Form(request.form)
    msg = "no result"
    if request.method == "POST":
        search_stock = request.form['stock']
        print(request.form)
        if search_stock == '':
            stocklist = ''
        else:
            cur = mysql.connection.cursor()
            result = cur.execute("SELECT * FROM stock where stock_symbol like %s or stock_name like%s", (search_stock+"%",search_stock+"%"))
            stocklist = cur.fetchall()
            cur.close()
        return render_template('stock_result.html', stocklist = stocklist)         
    return render_template('home.html',form=form)


# About
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/stock/<stock_symbol>/')
def stock_profile(stock_symbol):
    legend = 'price'
    overview = myiex.single_stock_overview(stock_symbol)
    chart =overview["chart"]
    quote = overview["quote"]
    company = overview["company"]
    prices = []
    previous = 0
    for i in chart:
        prices.append(i['open'] if 'open' in i else i['marketOpen'] if 'marketOpen' in i else previous)
        previous = prices[-1]
    # prices = [i['open'] if 'open' in i else i['marketOpen'] if 'marketOpen' in i else 0 for i in chart]
    volumes = [i['marketVolume'] for i in chart]
    data = {"prices":prices, "volumes":volumes}
    dtimes = [i['label'] for i in chart]
    return render_template('stock_profile.html', values=data, labels=dtimes, legend=legend, quote = quote, company = company)

#Single Article
@app.route('/article/<string:id>/')
def article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    return render_template('article.html', article=article)



# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    first_name = StringField('First Name', [validators.Length(min=1, max=50)])
    last_name = StringField('Last Name', [validators.Length(min=1, max=50)])
    DOB = DateField('DOB', format='%d-%m-%Y') #format='%d/%m/%y'
    gender = RadioField('Gender', choices = [('M','Male'),('F','Female')])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    #photo =
    



# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        first_name = form.first_name.data
        last_name = form.last_name.data
        DOB = form.DOB.data
        gender = form.gender.data
        email = form.email.data
        #photo = 

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(username, password, first_name, last_name, DOB, gender, email) VALUES(%s, %s, %s, %s, %s, %s, %s)", (username, password, first_name, last_name, DOB, gender, email))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['uid'] = data['id']

                flash('You are now logged in', 'success')
                return redirect(url_for('homepage'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            cur.close()
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/testportfolio/<username>')
def testportfolio(username, uid =None):
    summary = portfolioDAO.pf_summary(username = username)
    return jsonify(summary)

# User home page with portfolios displayed
@app.route('/myhomepage/',methods = ['GET','POST'])
@is_logged_in
def homepage():
    result = {}
    if request.method == 'POST':
        if request.form['action'] == 'add':
            if_added = portfolioDAO.add_portfolio(p_name = request.form["p_name"], uid = session['uid'])
            result['add'] = if_added
        if request.form['action'] == 'delete':
            if_deleted = portfolioDAO.delete_portfolio(p_name = request.form["p_name"], uid = session['uid'])
            result['delete'] = if_deleted
    summary, summary_index = portfolioDAO.pf_summary(uid = session["uid"])
    result['summary'] = summary
    result['summary_index'] = summary_index
    #return jsonify(result)
    return render_template('userhomepage.html', portfolios = result)

# @app.route('/portfolio/username=<username>&pfname=<p_name>/', methods=['POST','GET'])
# @is_logged_in
# def pf_details(username, p_name):
#     if session['username'] != username:
#         return redirect(url_for(homepage, username = session['username']))



# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()

# User Profile
@app.route('/profile/<username>',methods=['GET','POST'])
@is_logged_in
def profile(username):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get user
    result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
    user= cur.fetchone()
    
    current_user = session['username']
    cur.close()
    
    return render_template('profile.html', username=username,user=user,current_user=current_user)

# Edit User Profile
@app.route('/edit_profile/<username>',methods=['GET','POST'])
@is_logged_in
def edit_profile(username):
    # Create cursor
    cur = mysql.connection.cursor()
    # Get article by id
    result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    cur.close()
    # Get form
    form = RegisterForm(request.form)
    # Populate detail form fields
    #form.first_name.data = user['first_name']
    #form.last_name.data = user['last_name']
    #form.DOB.data = user['DOB']
    #form.gender.data = user['gender']
    #form.email.data = user['email']
    if request.method == "POST":
        password = sha256_crypt.encrypt(str(form.password.data))
        first_name = form.first_name.data
        last_name = form.last_name.data
        DOB = form.DOB.data
        gender = form.gender.data
        email = form.email.data
        #photo =
        print (first_name) 
        # Create cursor
        cur = mysql.connection.cursor()
        # Execute query
        cur.execute ("UPDATE users SET password=%s, first_name=%s, last_name=%s, DOB=%s, gender=%s, email=%s WHERE username=%s ",(password, first_name, last_name, DOB, gender, email, username))
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()  
        flash('Profile detail Updated', 'success')  
        return redirect(url_for("profile",username=username))    
    return render_template('edit_profile.html', user=user,username=username,form=form)

# User Search
@app.route('/search_user',methods=['GET','POST'])
@is_logged_in
def search_user():
    #form = Form(request.form)
    if request.method == "POST":
        # Get Form Fields
        search_user = request.form['name']
        current_user = session['username']
        tempUsers = ""
        followed = ""
        if search_user != "":
            cur = mysql.connection.cursor()
            values = search_user.split(" ")
            num = len(values)
            if num == 1:
                name = values[0]
                tempUsers = userDAO.getByFirstName(name,cur)
                tempUsers=list(tempUsers)
                tempUsers.extend(list(userDAO.getByLastName(name,cur)))
                print(tempUsers)
            elif num == 2:
                tempUsers = userDAO.getByBothName(values,cur)

            if tempUsers != "":
                followed = followDAO.getIdolId(current_user,cur)
            #Close connection

            cur.close()
        return render_template('user_result.html', current_user=current_user,result=tempUsers, followed=followed)
    return render_template('search_user.html')

# User result
@app.route('/user_result',methods=['GET','POST'])
@is_logged_in
def user_result():
    if request.method == "POST":
        cur = mysql.connection.cursor()
        if request.form['submit'] == "Follow":
            # Get Form Fields
            user_be_followed = request.form['idol']      
            follow_by_user = userDAO.getID(session['username'], cur)
            # Execute query
            cur.execute("INSERT INTO follow(idol, follower) VALUES(%s, %s)", (user_be_followed, follow_by_user))
        elif request.form['submit'] == "Unollow":
            # Get Form Fields
            user_be_followed = request.form['idol']      
            follow_by_user = userDAO.getID(session['username'], cur)
            # Execute query
            cur.execute("DELETE FROM follow where idol = %s and follower = %s", (user_be_followed, follow_by_user))
        # Commit to DB
        mysql.connection.commit()
        #Close connection
        cur.close()
        return render_template('search_user.html')
    return render_template('search_user.html')

# # Add Article
# @app.route('/add_article', methods=['GET', 'POST'])
# @is_logged_in
# def add_article():
#     form = ArticleForm(request.form)
#     if request.method == 'POST' and form.validate():
#         title = form.title.data
#         body = form.body.data
#
#         # Create Cursor
#         cur = mysql.connection.cursor()
#
#         # Execute
#         cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))
#
#         # Commit to DB
#         mysql.connection.commit()
#
#         #Close connection
#         cur.close()
#
#         flash('Article Created', 'success')
#
#         return redirect(url_for('dashboard'))
#
#     return render_template('add_article.html', form=form)
#
#
# # Edit Article
# @app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
# @is_logged_in
# def edit_article(id):
#     # Create cursor
#     cur = mysql.connection.cursor()
#
#     # Get article by id
#     result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
#
#     article = cur.fetchone()
#     cur.close()
#     # Get form
#     form = ArticleForm(request.form)
#
#     # Populate article form fields
#     form.title.data = article['title']
#     form.body.data = article['body']
#
#     if request.method == 'POST' and form.validate():
#         title = request.form['title']
#         body = request.form['body']
#
#         # Create Cursor
#         cur = mysql.connection.cursor()
#         app.logger.info(title)
#         # Execute
#         cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
#         # Commit to DB
#         mysql.connection.commit()
#
#         #Close connection
#         cur.close()
#
#         flash('Article Updated', 'success')
#
#         return redirect(url_for('dashboard'))
#
#     return render_template('edit_article.html', form=form)
#
# # Delete Article
# @app.route('/delete_article/<string:id>', methods=['POST'])
# @is_logged_in
# def delete_article(id):
#     # Create cursor
#     cur = mysql.connection.cursor()
#
#     # Execute
#     cur.execute("DELETE FROM articles WHERE id = %s", [id])
#
#     # Commit to DB
#     mysql.connection.commit()
#
#     #Close connection
#     cur.close()
#
#     flash('Article Deleted', 'success')
#
#     return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
