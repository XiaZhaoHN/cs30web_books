import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create table books
db.execute("DROP TABLE IF EXISTS books")
db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY, isbn varchar(10) NOT NULL, title varchar(50), author varchar(50), year varchar(4))")

# Read csv and insert into db table
def main():
	f = open("test.csv")
	reader = csv.reader(f)
	i = 0
	for isbn, title, author, year in reader:
		db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
			{"isbn":isbn, "title":title, "author":author, "year":year})
		print(i)
		i = i + 1
	books = db.execute("SELECT * FROM books").fetchall()
	for book in books:
		print(f"book {title} is written by {author} on {year}")
	db.commit()

if __name__ == "__main__":
    main()
