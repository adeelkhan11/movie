from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
import datetime
import re
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movie'

    id = Column(String(50), primary_key=True)
    category = Column(String(50))
    name = Column(String(100))
    genre = Column(String(50))
    year = Column(Integer)
    description = Column(String(4000))
    keywords = Column(String(4000))
    score = Column(DECIMAL(5, 2))
    rating = Column(String(50))
    rating_au = Column(String(50))
    duration = Column(Integer)
    country = Column(String(50))
    language = Column(String(100))
    advisory_nudity = Column(String(50))
    advisory_violence = Column(String(50))
    advisory_profanity = Column(String(50))
    advisory_alcohol = Column(String(50))
    advisory_frightening = Column(String(50))
    cast = Column(String(500))
    gross = Column(Integer)
    image = Column(String(250))
    updated_date = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)


def main():
    import requests
    from bs4 import BeautifulSoup
    page = requests.get(f'https://www.imdb.com/chart/top/')
    soup = BeautifulSoup(page.content, 'html.parser')
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///../data/movie.db')

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)

    DBSession = sessionmaker(bind=engine)

    session = DBSession()

    # movie = Movie(id='tt0111161')
    # session.add(movie)
    for a in soup.select('td.titleColumn a'):
        m = re.match('/title/([^/]+)/', a.attrs['href'])
        if m is not None:
            movie_id = m.group(1)
            if session.query(Movie).filter(Movie.id == movie_id).scalar() is None:
                print(movie_id)
                new_movie = Movie(id=movie_id)
                session.add(new_movie)
    session.commit()


if __name__ == '__main__':
    main()
