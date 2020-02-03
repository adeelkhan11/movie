import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="movie-info-akhan", # Replace with your own username
    version="0.0.1",
    author="Adeel Khan",
    author_email="adeelkhan11@gmail.com",
    description="This package scrapes parental guide info for movies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests>=2.22.0',
        'beautifulsoup4>=4.8.2',
        'SQLAlchemy>=1.3.12',
        'jinja2>=2.10.3',
        'markdown2>=2.3.8',
        'SQLAlchemy-Paginator>=0.1'
    ],
    python_requires='>=3.5'
)
