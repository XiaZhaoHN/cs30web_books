import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash
from datetime import datetime

#import urllib.parse as urlparse
import csv

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#db.execute("DROP TABLE IF EXISTS users")
db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, hash VARCHAR NOT NULL)")

#db.execute("DROP TABLE IF EXISTS comments")
db.execute("CREATE TABLE comments(id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, book_id INTEGER REFERENCES books, rate INTEGER, comment VARCHAR NOT NULL, timestamp TIMESTAMP NOT NULL)")
db.commit()
