from flask import Flask, render_template

app = Flask(__name__)
app.debug = True


@app.route('/')
def hello():
    return render_template("home.html")


@app.route('/index')
def index():
    return "<h1>Hello, FlaskApp User =)!</h1>"
