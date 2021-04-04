import setuptools

with open("README.md", "r") as file:
    readme = file.read()

setuptools.setup(
    name="ff.net-api",
    version="1.3",
    author="Jack Ashwell",
    author_email="jack.ashwell1@gmail.com",
    description="An API to access various parts of FF.net",
    long_description=readme,
    python_requires='>=3.8',
    install_requires=[
        "BeautifulSoup4",
        "cloudscraper"
    ],
    url="https://github.com/Aspect1103/FanFiction.net-Scraper",
    packages=["FFScraper"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)