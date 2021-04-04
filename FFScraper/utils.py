from . import Story
import cloudscraper
import time
from bs4 import BeautifulSoup

class FFInvalidLink(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass

class CloudflareError(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass

class InvalidChapterID(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass

class WorkNotLoaded(Exception):
    def __init__(self, message):
        super().__init__(message)
        pass


def game(name, rate_limit=2):
    _scraper = cloudscraper.CloudScraper(browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False,
        "desktop": True
    })
    try:
        request = _scraper.get(f"https://www.fanfiction.net/game/{name}")
    except cloudscraper.exceptions.CloudflareChallengeError:
        raise CloudflareError("A Cloudflare version 2 check has been detected. Please try again in a little while")
    tempSoup = BeautifulSoup(request.text, features="lxml")
    pageHrefs = tempSoup.find("center", {"style": "margin-top:5px;margin-bottom:5px;"}).find_all("a", href=True)
    maxPage = str(pageHrefs[len(pageHrefs)-2]).split("=")[4].split('"')[0]
    ficLinks = []
    for page in range(int(maxPage)):
        time.sleep(rate_limit)
        try:
            request = _scraper.get(f"https://www.fanfiction.net/game/{name}/?p={page+1}")
            tempSoup = BeautifulSoup(request.text, features="lxml")
            ficsRaw = tempSoup.find_all("div", {"class": "z-list zhover zpointer"})
            for fic in ficsRaw:
                hrefRaw = BeautifulSoup(str(fic), features="lxml").find("a", href=True)
                splittedTags = str(hrefRaw).split("/")
                f"https://www.fanfiction.net/s/{splittedTags[2]}"
                ficLinks.append(Story.Story(f"https://www.fanfiction.net/s/{splittedTags[2]}", loaded=False))
        except cloudscraper.exceptions.CloudflareChallengeError:
            raise CloudflareError("A Cloudflare version 2 check has been detected. Please try again in a little while")
    return ficLinks