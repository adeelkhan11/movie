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
                    order_by(Movie.score.desc()),
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
                    order_by(Movie.score.desc()),
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

for l in movie_lists:
    generate_list(index_template, *(l[x] for x in ('name', 'folder', 'query', 'description')))

copyfile('templates/grid.css', f'{OUTPUT_DIR}/grid.css')
index_template = env.get_template('index.html')
index_html_content = index_template.render(title='Adeel\'s Movie Lists',
                                           description='Lists of clean movies as rated by IMDB\'s Parental Guides.',
                                           items=movie_lists)
file_name = 'index.html'
with open(f'{OUTPUT_DIR}/{file_name}', 'w') as file:
    file.write(index_html_content)

exit()
query = (session.query(Movie).filter(Movie.name != None).
         filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
         filter(Movie.advisory_frightening.in_(['None', 'Mild', 'Moderate'])).
         filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
         filter(Movie.year >= 1950).
         filter(Movie.duration >= 60).
         filter(Movie.language.like('English%')).
         filter(Movie.gross >= 7000000).
         order_by(Movie.score.desc()))

env = Environment(loader=PackageLoader('ssg', 'templates'))
index_template = env.get_template('movies.html')
for page in range(12):
    start, stop = PAGE_SIZE * page, PAGE_SIZE * (page + 1)
    movies = query.slice(start, stop).all()
    if movies is None:
        break
    index_html_content = index_template.render(rank=PAGE_SIZE * page, items=movies, page=page + 1)
    file_name = 'index.html' if page == 0 else f'movies-{page + 1}.html'
    with open(f'movies_older/{file_name}', 'w') as file:
        file.write(index_html_content)
    if len(movies) < PAGE_SIZE:
        break

query = (session.query(Movie).filter(Movie.name != None).
         filter(Movie.advisory_nudity.in_(['None'])).
         filter(Movie.advisory_frightening.in_(['None', 'Mild', 'Moderate'])).
         filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
         filter(Movie.year >= 1950).
         filter(Movie.duration >= 60).
         filter(Movie.language.like('English%')).
         filter(Movie.gross >= 7000000).
         order_by(Movie.score.desc()))

env = Environment(loader=PackageLoader('ssg', 'templates'))
index_template = env.get_template('movies.html')
for page in range(12):
    start, stop = PAGE_SIZE * page, PAGE_SIZE * (page + 1)
    movies = query.slice(start, stop).all()
    if movies is None:
        break
    index_html_content = index_template.render(rank=PAGE_SIZE * page, items=movies, page=page + 1)
    file_name = 'index.html' if page == 0 else f'movies-{page + 1}.html'
    with open(f'movies_big_kids/{file_name}', 'w') as file:
        file.write(index_html_content)
    if len(movies) < PAGE_SIZE:
        break

query = (session.query(Movie).filter(Movie.name != None).
         filter(Movie.advisory_nudity.in_(['None', 'Mild'])).
         # filter(Movie.advisory_frightening.in_(['None', 'Mild', 'Moderate'])).
         # filter(Movie.advisory_profanity.in_(['None', 'Mild', 'Moderate'])).
         filter(Movie.year >= 1950).
         filter(Movie.duration >= 60).
         filter(Movie.language.like('English%')).
         filter(Movie.gross >= 7000000).
         order_by(Movie.score.desc()))

env = Environment(loader=PackageLoader('ssg', 'templates'))
index_template = env.get_template('movies.html')
for page in range(12):
    start, stop = PAGE_SIZE * page, PAGE_SIZE * (page + 1)
    movies = query.slice(start, stop).all()
    if movies is None:
        break
    index_html_content = index_template.render(rank=PAGE_SIZE * page, items=movies, page=page + 1)
    file_name = 'index.html' if page == 0 else f'movies-{page + 1}.html'
    with open(f'movies_full/{file_name}', 'w') as file:
        file.write(index_html_content)
    if len(movies) < PAGE_SIZE:
        break

exit()
for i, movie in enumerate(session.query(Movie).filter(Movie.name != None).
                                  filter(Movie.advisory_nudity == 'None').
                                  filter(Movie.advisory_frightening.in_(['None', 'Mild'])).
                                  filter(Movie.advisory_profanity.in_(['None', 'Mild'])).
                                  filter(Movie.year >= 1970).
                                  filter(Movie.duration >= 60).
                                  filter(Movie.language.like('English%')).
                                  order_by(Movie.score.desc()).all(),
                          start=1):
    print(movie.name)

movies = list(session.query(Movie).filter(Movie.name != None).
              filter(Movie.advisory_nudity == 'None').
              filter(Movie.advisory_frightening.in_(['None', 'Mild'])).
              filter(Movie.advisory_profanity.in_(['None', 'Mild'])).
              filter(Movie.year >= 1970).
              filter(Movie.duration >= 60).
              filter(Movie.language.like('English%')).
              order_by(Movie.score.desc()).all())

exit()
POSTS = {}
for markdown_post in os.listdir('content'):
    file_path = os.path.join('content', markdown_post)

    with open(file_path, 'r') as file:
        POSTS[markdown_post] = markdown(file.read(), extras=['metadata', 'tables'])

POSTS = {
    post: POSTS[post] for post in
    sorted(POSTS, key=lambda post: datetime.strptime(POSTS[post].metadata['date'], '%Y-%m-%d  %H:%M'), reverse=True)
}

env = Environment(loader=PackageLoader('ssg', 'templates'))
index_template = env.get_template('index.html')
post_template = env.get_template('post-detail.html')
tweeps_template = env.get_template('tweeps.html')

people = [{'screen_name': 'coolbob', 'name': 'Bob', 'address': '1 George St', 'phone': '12345678'},
          {'screen_name': 'joe_12', 'name': 'Joe', 'address': '5 Lee St', 'phone': '46755678'},
          {'screen_name': 'rayman', 'name': 'Ray', 'address': '103 Pitt St', 'phone': '45999478'}]

tweeps_html_content = tweeps_template.render(trend='Success Yay', items=people)
with open('output/tweeps.html', 'w') as file:
    file.write(tweeps_html_content)

index_posts_metadata = [POSTS[post].metadata for post in POSTS]

index_html_content = index_template.render(posts=index_posts_metadata)

with open('output/index.html', 'w') as file:
    file.write(index_html_content)

# render each post and write it to output/posts/<post.slug>/index.html
for post in POSTS:
    post_metadata = POSTS[post].metadata

    post_data = {
        'content': POSTS[post],
        'title': post_metadata['title'],
        'date': post_metadata['date'],
    }

    post_html_content = post_template.render(post=post_data)

    post_file_path = 'output/posts/{slug}/index.html'.format(slug=post_metadata['slug'])

    os.makedirs(os.path.dirname(post_file_path), exist_ok=True)
    with open(post_file_path, 'w') as file:
        file.write(post_html_content)
