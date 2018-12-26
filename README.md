# Project 1: Books
This is a flask web server to search for book information and give feedback.

## Files
- application.py: The flask application
- import.py: Python script to import books.
- db_tables.py:  Python script to create DB tables.
- static/style.css: The local CSS stylesheet.
- templates: Contains HTML files.
- books.csv: The book records to be imported by import.py
- requirements.txt: Python packages to be installed for this project.

## Settings
1. Run `pip install -r requirements.txt` in terminal window to install necessary packages
2. Set environment variable FLASK_APP to be application.py
3. Set environment variable DATABASE_URL to be the URL of your database
4. Run `python import.py` to create a book table in the database and import books from books.csv
5. Run `python db_tables.py` to create other tables in the database
6. Run `flask run` to start the app.

When all steps are complete, open a window in the web browser, go to `https://localhost:5000` to use the app.

## Usage
`/register`: To register a new user account
`/login`: To login an existing user
`/`: The search page
`/books`: The results from search page
`/books/{isbn number}`: A detailed page of a book. User can rate and comment, but only once for each book per user
`/api/{isbn number}`: An api for a book, returns a json response. When no matches, returns 404
