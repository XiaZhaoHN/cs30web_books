import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create table books
# db.execute("DROP TABLE IF EXISTS books")
db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY, isbn varchar(10) NOT NULL, title varchar(50), author varchar(50), year varchar(4))")

# Read csv and insert into db table
def main():
	f = open("books.csv")
	reader = csv.reader(f)
	i = 0
	for isbn, title, author, year in reader:
		db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
			{"isbn":isbn, "title":title, "author":author, "year":year})
		db.commit()
		print(i)
		i = i + 1


if __name__ == "__main__":
    main()
