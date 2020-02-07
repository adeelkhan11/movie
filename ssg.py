import math
import os
from datetime import datetime
from pathlib import Path
from shutil import copyfile

from jinja2 import Environment, PackageLoader
from markdown2 import markdown
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_paginator import Paginator

PAGE_SIZE = 50
OUTPUT_DIR = 'site'

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
from movie import Base, Movie


def generate_list(template, name, folder, query, description):
    Path(f'{OUTPUT_DIR}/{folder}').mkdir(parents=True, exist_ok=True)
    # copyfile('templates/grid.css', f'{OUTPUT_DIR}/{folder}/grid.css')
    page_count = min(math.ceil(query.count() / PAGE_SIZE), 12)
    for page in range(page_count):
        start, stop = PAGE_SIZE * page, PAGE_SIZE * (page + 1)
        movies = query.slice(start, stop).all()
        if movies is None:
            break
        html_content = template.render(title=name, description=description, rank=PAGE_SIZE * page,
                                       items=movies, page=page + 1, page_count=page_count)
        file_name = 'index.html' if page == 0 else f'movies-{page + 1}.html'
        with open(f'{OUTPUT_DIR}/{folder}/{file_name}', 'w') as file:
            file.write(html_content)
        if len(movies) < PAGE_SIZE:
            break


engine = create_engine('sqlite:///data/movie.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)

session = DBSession()

movie_lists = [{'name': 'Family Movies',
                'folder': 'family',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity == 'None').
                    filter(Movie.advisory_frightening.in_(['None', 'Mild'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild'])).
                    filter(Movie.year >= 1950).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 7000000).
                    order_by(Movie.score.desc()).
                    order_by(Movie.gross.desc()),
                'description': 'Language and Horror is limited to Mild and Nudity is limited to None.'},
               {'name': 'Movies for Grown Ups',
                'folder': 'grown-ups',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
                    filter(Movie.advisory_frightening.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.year >= 1950).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 7000000).
                    order_by(Movie.score.desc()).
                    order_by(Movie.gross.desc()),
                'description': 'Language and Horror is limited to Moderate and Nudity is limited to Mild.'},
               {'name': 'Highest Grossing Movies for Grown Ups',
                'folder': 'grown-ups-by-earnings',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
                    filter(Movie.advisory_frightening.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.year >= 1950).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 7000000).
                    order_by(Movie.gross.desc()),
                'description': 'This list shows the highest grossing movies. Language and Horror is limited to Moderate and Nudity is limited to Mild.'},
               {'name': 'Classics',
                'folder': 'pre-1970',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.year < 1970).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 2000000).
                    order_by(Movie.score.desc()).
                    order_by(Movie.gross.desc()),
                'description': 'Movies that were released before 1970. Language is limited to Moderate and Nudity is limited to Mild.'},
               {'name': 'Released between 1970 and 1989',
                'folder': '1970-1989',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.year >= 1970).
                    filter(Movie.year < 1990).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 5000000).
                    order_by(Movie.score.desc()).
                    order_by(Movie.gross.desc()),
                'description': 'Movies that were released between 1970 and 1989. Language is limited to Moderate and Nudity is limited to Mild.'},
               {'name': 'Released between 1990 and 1999',
                'folder': '1990-1999',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.year >= 1990).
                    filter(Movie.year < 2000).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 7000000).
                    order_by(Movie.score.desc()).
                    order_by(Movie.gross.desc()),
                'description': 'Movies that were released in the 1990s. Language is limited to Moderate and Nudity is limited to Mild.'},
               {'name': 'Released between 2000 and 2009',
                'folder': '2000-2009',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.year >= 2000).
                    filter(Movie.year < 2010).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 9000000).
                    order_by(Movie.score.desc()).
                    order_by(Movie.gross.desc()),
                'description': 'Movies that were released between 2000 and 2009. Language is limited to Moderate and Nudity is limited to Mild.'},
               {'name': 'Released after 2010',
                'folder': '2010-2019',
                'query': session.query(Movie).filter(Movie.name != None).
                    filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
                    filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
                    filter(Movie.year >= 2010).
                    filter(Movie.duration >= 60).
                    filter(Movie.language.like('English%')).
                    filter(Movie.gross >= 10000000).
                    order_by(Movie.score.desc()).
                    order_by(Movie.gross.desc()),
                'description': 'Movies that were released after 2010. Language is limited to Moderate and Nudity is limited to Mild.'}
               ]

env = Environment(loader=PackageLoader('ssg', 'templates'))
index_template = env.get_template('movies.html')

for l in movie_lists[:1]:
    generate_list(index_template, *(l[x] for x in ('name', 'folder', 'query', 'description')))

copyfile('templates/grid.css', f'{OUTPUT_DIR}/grid.css')
index_template = env.get_template('index.html')
index_html_content = index_template.render(title='Movie Lists',
                                           description='<p>Lists of clean movies as rated by IMDB\'s Parental Guides.</p><p>'
                                           'These are top rated movies, for people who are concerned about what they or their children watch.</p>'
                                           '<p>The parental guide ratings are clearly visible and colour coded to allow easy browsing.</p>',
                                           items=movie_lists)
file_name = 'index.html'
with open(f'{OUTPUT_DIR}/{file_name}', 'w') as file:
    file.write(index_html_content)
