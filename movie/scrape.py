import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from movie import Movie, Base


def text(v, delimiter=', '):
    if isinstance(v, list):
        return delimiter.join([str(x) for x in v])
    else:
        return v


def scrape_text(soup, path):
    data = soup.select(path)
    if len(data) > 0:
        return data[0].get_text().strip()
    else:
        return None


def minutes_from_movie_time(time_text):
    result = None
    if time_text is not None:
        m = re.match('PT([0-9]+H)?([0-9]+M)?', time_text)
        if m is not None:
            hours = 0 if m.group(1) is None else int(m.group(1)[:-1])
            minutes = 0 if m.group(2) is None else int(m.group(2)[:-1])
            result = (hours * 60) + minutes
    return result


def scrape_movie_details(movie, session, counter):
    page = requests.get(f'https://www.imdb.com/title/{movie.id}/')
    if page.status_code == 404:
        movie.name = 'Error: Page not found'
        print(f'Warning: {movie.id} not found.')
        return
    soup = BeautifulSoup(page.content, 'html.parser')
    data = json.loads(soup.find('script', type='application/ld+json').text)

    movie.category = data.get('@type')
    movie.name = data.get('name')
    m = re.match('(.+) \(', soup.find('meta', property='og:title').get('content'))
    if m is not None:
        movie.name = m.group(1)
    movie.image = data.get('image')
    movie.genre = text(data.get('genre'))
    movie.rating = data.get('contentRating')
    actor = data.get('actor')
    if isinstance(actor, list):
        movie.cast = ', '.join([a['name'] for a in actor])
    elif isinstance(actor, dict):
        movie.cast = actor.get('name')
    movie.description = soup.find('meta', property='og:description').get('content')
    description = scrape_text(soup, 'div#titleStoryLine div.canwrap p span')
    if description is not None:
        movie.description = description
    publish_date = data.get('datePublished')
    if publish_date is not None:
        movie.year = int(data.get('datePublished')[:4])
    movie.keywords = data.get('keywords')
    ar = data.get('aggregateRating')
    if ar is not None:
        movie.score = ar.get('ratingValue')
    movie.duration = minutes_from_movie_time(data.get('duration'))

    # title = soup.find_all('h1')[0].get_text().strip()
    # score = float(soup.select('strong span')[0].get_text())
    rating_au = soup.select('div.subtext')[0].get_text().split('|')[0].strip()
    if not re.match('[0-9]+(h|min)', rating_au) and ',' not in rating_au and len(rating_au) <= 7:
        movie.rating_au = rating_au
    # print(title)
    # print(score)
    # print(rating)
    country, language = [], []
    for a in soup.select('div#titleDetails div a'):
        if 'country_of_origin' in a.attrs['href']:
            country.append(a.get_text())
        if 'primary_language' in a.attrs['href']:
            language.append(a.get_text())
    for a in soup.select('div#titleDetails div'):
        line = text(a.contents, ';')
        if 'Gross' in line:
            m = re.search('\$([0-9,])+', line)
            if m is not None:
                m = re.search('\$([0-9,]+)', line)
                if m is not None:
                    movie.gross = m.group(1).replace(',', '')
    movie.country = ', '.join(country)
    movie.language = ', '.join(language)

    pg = requests.get(f'https://www.imdb.com/title/{movie.id}/parentalguide')
    pgs = BeautifulSoup(pg.content, 'html.parser')

    parental_guide_types = ['advisory-nudity',
                            'advisory-violence',
                            'advisory-profanity',
                            'advisory-alcohol',
                            'advisory-frightening']
    parental_guide = dict()
    try:
        for pgt in parental_guide_types:
            parental_guide[pgt] = pgs.select_one(
                f'section#{pgt} ul li div label div div span.ipl-status-pill').get_text()

        movie.advisory_nudity = parental_guide.get('advisory-nudity')
        movie.advisory_violence = parental_guide.get('advisory-violence')
        movie.advisory_profanity = parental_guide.get('advisory-profanity')
        movie.advisory_alcohol = parental_guide.get('advisory-alcohol')
        movie.advisory_frightening = parental_guide.get('advisory-frightening')
        print(f'{counter:4}. {movie.name} ({movie.year}) [{movie.country}:{movie.language}]')
    except AttributeError:
        print(f'{counter:4}. {movie.name}: Parental advisory not available.')

    if movie.country not in ('China', 'Japan', 'Soviet Union', 'South Africa', 'France',
                             'Iran', 'Bulgaria', 'Spain', 'Belgium', 'Denmark', 'Germany',
                             'Russia', 'Italy', 'Netherlands', 'Sweden', 'Mexico', 'Poland', 'Turkey',
                             'Argentina', 'South Korea') \
            and movie.advisory_nudity != 'Severe' \
            and (movie.genre is None or 'Horror' not in movie.genre) \
            and (movie.language is None or 'English' in movie.language or 'Urdu' in movie.language or 'Hindi' in movie.language):
        for t in soup.select('div#title_recs div div div div div.rec_item a'):
            m = re.match('/title/([^/]+)/', t.attrs['href'])
            if m is not None:
                movie_id = m.group(1)
                if session.query(Movie).filter(Movie.id == movie_id).scalar() is None:
                    print(f'        {movie_id}')
                    new_movie = Movie(id=movie_id)
                    session.add(new_movie)
        # print(t.attrs['href'])


def main():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///../data/movie.db')

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)

    DBSession = sessionmaker(bind=engine)

    session = DBSession()

    # movie = Movie(id='tt0111161')
    for i, movie in enumerate(session.query(Movie).filter(Movie.name == None).order_by(Movie.updated_date).all(),
                              start=1):
        scrape_movie_details(movie, session, i)
        # session.add(movie)
        if i % 20 == 0:
            print('Saving data... ', end='')
            session.commit()
            print('Done.')
            sleep(5)
        else:
            sleep(3)
        if i >= 220:
            break
    print('Saving data... ', end='')
    session.commit()
    print('Done.')


if __name__ == '__main__':
    main()
