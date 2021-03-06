from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    session
)
from flask_mysqldb import MySQL
from wtforms import (
    Form,
    StringField,
    PasswordField,
    validators,
)
from passlib.hash import sha256_crypt
from functools import wraps
from my_settings import *
from data import articles

app = Flask(__name__)
app.debug = True

# Secret key:
app.secret_key = SECRET_KEY


# Config MySQL:
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = MYSQL_CURSORCLASS

# Init MySQL
mysql = MySQL(app)


objects = articles()


# Home page
@app.route('/')
def home():
    return render_template("home.html")


# About page
@app.route('/about')
def about():
    return render_template("about.html")


# Articles List
@app.route('/articles')
def articles():
    return render_template("articles.html", articles=objects)


# Single Article
@app.route('/article/<string:id>')
def article(id):
    return render_template("article.html", id=id)


# Register Form Class
class RegisterForm(Form):
    name = StringField(u'Name', validators=[
        validators.input_required(),
        validators.Length(min=1, max=50)
    ])
    email = StringField(u'Email', validators=[
        validators.Length(min=6, max=50)
    ])
    username = StringField(u'Username', validators=[
        validators.Length(min=3, max=25)
    ])
    password = PasswordField(u'Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords don\'t match')
    ])
    confirm_password = PasswordField(u'Confirm password')


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password)"
                    " VALUES (%s, %s, %s, %s)",
                    (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Thanks for registering', 'success')

        form = RegisterForm()
        return redirect(url_for('home'))
    return render_template("registration/register.html", form=form)


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
        result = cur.execute("SELECT * FROM users WHERE username = %s",
                             [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('registration/login.html', error=error)

        else:
            error = 'Username not found'
            return render_template('registration/login.html', error=error)

    return render_template("registration/login.html")


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized. Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# User logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')
