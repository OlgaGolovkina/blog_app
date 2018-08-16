from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    url_for,
    request
)
from flask_mysqldb import MySQL
from wtforms import (
    Form,
    StringField,
    PasswordField,
    validators,
)
from passlib.hash import sha256_crypt
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


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/articles')
def articles():
    return render_template("articles.html", articles=objects)


@app.route('/article/<string:id>')
def article(id):
    return render_template("article.html", id=id)


class RegisterForm(Form):
    name = StringField(u'Name', validators=[
        validators.input_required(),
        validators.Length(min=1, max=50)
    ])
    email = StringField(u'Email', validators=[validators.Length(min=6,
                                                                max=50)])
    username = StringField(u'Username', validators=[validators.Length(min=3,
                                                                      max=25)])
    password = PasswordField(u'Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords do not'
                                                       ' match')
    ])
    confirm_password = PasswordField(u'Confirm password')


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
