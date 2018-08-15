from flask import Flask, render_template
from data import articles

app = Flask(__name__)
app.debug = True

objects = articles()


@app.route('/')
def hello():
    return render_template("home.html")


@app.route('/index')
def index():
    return "<h1>Hello, FlaskApp User =)!</h1>"


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/articles')
def articles():
    return render_template("articles.html", articles=objects)


# @app.route('/articles/<string:id>')
# def articles(id):
#     return render_template("articles.html", id=id)
