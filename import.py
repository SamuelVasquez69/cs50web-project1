import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

os.environ['DATABASE_URL']='postgres://egtusoaqicdabv:1d8d78b9a957560fafc4d26c218390929934c01a463c6e05e14e9b0c8e7022c8@ec2-52-2-118-38.compute-1.amazonaws.com:5432/d174ofjmjit41'
os.environ['FLASK_DEBUG']='1'
os.environ['FLASK_APP']='application.py'

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO flights (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Libros agregado isbn {isbn} title {title} author {author} year {year} ")
    db.commit()

if __name__ == "__main__":
    main()