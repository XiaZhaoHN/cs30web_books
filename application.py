import os
import requests
import json

from functools import wraps
from flask import Flask, flash, redirect, session, render_template, request, jsonify
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Goodreads API key
API_KEY = "zgUvtPRLDq7lSh0LumqQbQ"


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app = Flask(__name__)


# Configure session
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# function to require login
def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Method to handle /api/isbn error request
class InvalidUsage(Exception):
    def __init__(self, status_code, message, payload=None):
        Exception.__init__(self)
        self.status_code = status_code
        self.message = message
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status_code'] = self.status_code
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")


@app.route("/books", methods=["GET", "POST"])
@login_required
def books():
    if request.method == "POST":

        # Check submitting no value
        if not request.form.get("q"):
            return render_template("error.html", message="Please fill a value in the form")

        # Taking user input with wildcard for query
        q = "%" + str(request.form.get("q")) + "%"

        books = db.execute("SELECT * FROM books WHERE isbn LIKE :q OR title LIKE :q OR author LIKE :q",
                           {"q": q, "q": q, "q": q}).fetchall()

        if (len(books) > 0):
            return render_template("books.html", books=books)
        else:
            return render_template("error.html", message="Book does not exist...")
    else:
        return render_template("index.html")


@app.route("/books/<string:isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    if book is None:
        return render_template("error.html", message="Book not exist")
    else:
        # default value
        reviews_count = 0
        average_rating = 'N/A'

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": isbn}).json()

        # Override default values if exists
        try:
            reviews_count = res["books"][0]["reviews_count"]
            average_rating = res["books"][0]["average_rating"]
        except TypeError:
            print("Value not available")

        comments = db.execute("SELECT username, comment, rate, timestamp FROM comments JOIN users ON comments.user_id = users.id WHERE book_id = :book_id",
                               {"book_id":book["id"]}).fetchall()

        # Take user input and insert into DB
        if request.method == "POST":
            existing_comm = db.execute("SELECT * FROM comments WHERE user_id = :user_id AND book_id = :book_id", {"user_id": session["user_id"], "book_id": book["id"]}).fetchall()

            # Check if user already rated
            if len(existing_comm) != 0:
                return "You have already rated for this book"
            else:
                db.execute("INSERT INTO comments(user_id, book_id, rate, comment, timestamp) VALUES (:user_id, :book_id, :rate, :comment, :timestamp)",
                            {"user_id": session["user_id"], "book_id": book["id"], "rate": request.form.get("rate"), "comment": request.form.get("comment"),
                            "timestamp": str(datetime.now())[:19]})
                # Commit DB insertion
                db.commit()
                comments = db.execute("SELECT username, comment, rate, timestamp FROM comments JOIN users ON comments.user_id = users.id WHERE book_id = :book_id",
                                       {"book_id":book["id"]}).fetchall()

        return render_template("book.html", isbn=isbn, book=book, reviews_count=reviews_count, average_rating=average_rating, comments=comments)


@app.route("/api/<string:isbn>")
@login_required
def api(isbn):
    book = db.execute("SELECT * from books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    if book is None:
        raise InvalidUsage(404, 'The requested ISBN number isn’t in your database')
        #return render_template("error.html", message="Book does not exist")
    else:
        reviews_count = 0
        average_rating = 'N/A'
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": API_KEY, "isbns": isbn}).json()

        try:
            reviews_count = res["books"][0]["reviews_count"]
            average_rating = res["books"][0]["average_rating"]
        except TypeError:
            print("Value not available")

        x = {"title": book.title, "author": book.author, "year": book.year, "isbn": isbn, "review_count": reviews_count, "average_score": average_rating}
        return json.dumps(x)


@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("password") == request.form.get("confirmation"):
            return "Passwords do not match"

        existing_users = db.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchall()

        if len(existing_users) != 0:
            return "Username taken"

        # Query database for username
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                         {"username": request.form.get("username"),
                          "hash": generate_password_hash(request.form.get("password"))})

        row = db.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchone()
        db.commit()

        session["user_id"] = row["id"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchall()

        # Check if username exists and correct password
        if len(rows) != 1 or check_password_hash(rows[0]["hash"], request.form.get("password")) == "false":
            return "Invalid username or password"

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    return redirect("/login")
