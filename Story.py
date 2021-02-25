from . import exceptions
import cloudscraper
from bs4 import BeautifulSoup
import datetime
import time
import re


class Story:
    def __init__(self, link, rate_limit=0):
        self.soup = None
        self.id = 0
        self.scraper = cloudscraper.CloudScraper(browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False,
            "desktop": True
        })
        self.metadata = None
        if True:
            _soup = self.requester(link, rate_limit)
            metadataRaw = _soup.find("span", {"class": "xgray xcontrast_txt"})
            self.metadata = str(metadataRaw).split(" - ")
            self.soup = _soup

    def requester(self, link, rate_limit):
        """
        Function to request a story's webpage

        Parameters:
            rate_limit (int): How long between each request

        Raises:
            exceptions.FFInvalidStoryLink: Invalid story url
            cloudscraper.exceptions.CloudflareChallengeError: Cloudflare version 2 challenge

        Returns:
            tempSoup (BeautifulSoup object): The story's webpage
        """
        self.id = self.getID(link)
        if self.id == None:
            raise exceptions.FFInvalidLink("Link is invalid")
        else:
            time.sleep(rate_limit)
            try:
                request = self.scraper.get(link)
            except cloudscraper.exceptions.CloudflareChallengeError:
                raise exceptions.CloudflareError("A Cloudflare version 2 has been detected."
                                                 " Please try again in a little while")
            tempSoup = BeautifulSoup(request.text, features="lxml")
            invalidStory = tempSoup.find("span", {"class": "gui_warning"})
            if invalidStory != None:
                raise exceptions.FFInvalidLink("Link is invalid")
            else:
                return tempSoup

    def getID(self, link):
        """
        Function to return a story's id

        Parameters:
            link (string): A story link

        Returns:
            id (int): A story's id
        """
        splitted = link.split("/")
        for split in splitted:
            if split.isdigit():
                return split

    def oneshot(self):
        """
        Function to return if a story is a oneshot or not

        Returns:
            oneshot (boolean): True if the story is a oneshot or false if it is not
        """
        request = self.requester(f"https://www.fanfiction.net/s/{self.id}/2", 0)
        try:
            oneshotTest = request.find("span", {"class": "gui_normal"}).text
            return True
        except AttributeError:
            return False

    def title(self):
        """
        Function to return a story's title

        Returns:
            title (string): A story's title
        """
        return self.soup.find("b", {"class": "xcontrast_txt"}).text

    def authors(self):
        """
        Function to return a story's authors

        Returns:
            authors (string): The story's authors
        """
        hrefList = self.soup.find_all("a", {"class": "xcontrast_txt"})
        if "/u/" in str(hrefList[1]):
            href = hrefList[1]["href"].replace("-", " ")
        else:
            href = hrefList[2]["href"].replace("-", " ")
        return f"https://www.fanfiction.net{href}"

    def fandoms(self):
        """
        Function to return a story's fandom

        Returns:
            fandom (string): The story's fandom
        """
        return self.soup.find_all("a", {"class": "xcontrast_txt"})[1].text

    def rating(self):
        """
        Function to return a story's rating

        Returns:
            rating (string): A story's rating
        """
        rating = BeautifulSoup(self.metadata[0], features="lxml")
        return rating.find("a").text

    def language(self):
        """
        Function to return a story's language

        Returns:
            language (string): A story's language
        """
        return self.metadata[1]

    def genre(self):
        """
        Function to return a story's genre

        Returns:
            genre (string): A story's genre
        """
        return self.metadata[2]

    def relationships(self):
        """
        Function to return a story's relationships

        Returns:
            relationships (string): A story's relationships
        """
        return self.metadata[3]

    def chapters(self):
        """
        Function to return a story's chapter count

        Returns:
            chapters (int): A story's chapter count
        """
        if self.oneshot():
            return 1
        return int(self.metadata[4][9:])

    def words(self):
        """
        Function to return a story's word count

        Returns:
            words (int): A story's word count
        """
        index = 5
        if self.oneshot():
            index -= 1
        if "Words" in self.relationships() or "Chapters" in self.relationships():
            index -= 1
        wordCount = self.metadata[index][7:]
        return int(wordCount.replace(",", ""))

    def reviews(self, chapter=0):
        """
        Function to return a story's reviews

        Parameters:
            chapter (int): The specific chapter to get reviews from. Default is 0 (every chapter)

        Raises:
            exceptions.InvalidChapterID: Invalid chapter number

        Returns:
            reviews (2D array): A story's reviews. Each individual array is in the format:
                [Username, chapter number, date, review text]
        """
        if chapter < 0 or chapter > self.chapters():
            raise exceptions.InvalidChapterID(f"{chapter} is not a valid chapter")
        reviewFinal = []
        retries = 5
        reviews = self.requester(f"https://www.fanfiction.net/r/{self.id}/{chapter}/", 0)
        try:
            maxPage = int(reviews.find_all("a")[121]["href"].split("/")[4])
        except IndexError:
            maxPage = 1
        for page in range(maxPage):
            if page > 0:
                try:
                    if retries > 0:
                        reviews = self.requester(f"https://www.fanfiction.net/r/{self.id}/{chapter}/{page}", 2)
                except cloudscraper.exceptions.CloudflareChallengeError:
                    retries -= 1
                    continue
            reviewList = reviews.find("table", {"class": "table table-striped"}).find_all("tr")
            for count, review in enumerate(reviewList):
                if count == 0:
                    pass
                else:
                    soup = BeautifulSoup(str(review), features="lxml")
                    try:
                        href = soup.find_all("a")[2]["href"]
                        username = f"https://www.fanfiction.net{href}"
                    except IndexError:
                        spanText = soup.find("td").getText()
                        chapterIndex = spanText.index("chapter")
                        username = spanText[1:chapterIndex-1]
                    chapterDateSplit = soup.find("small").text.split(" . ")
                    dateSplit = chapterDateSplit[1].split("/")
                    if len(dateSplit) == 2:
                        currentYear = datetime.datetime.now().year
                        datePosted = datetime.date(day=int(dateSplit[1]), month=int(dateSplit[0]), year=int(currentYear))
                    else:
                        datePosted = datetime.date(day=int(dateSplit[1]), month=int(dateSplit[0]), year=int(dateSplit[2]))
                    result = [
                        username,
                        chapterDateSplit[0][8:],
                        datePosted,
                        [self.cleaner(soup.find("div").text)]
                    ]
                    reviewFinal.append(result)
        return reviewFinal

    def favourites(self):
        """
        Function to return how many favourites a story has

        Returns:
            favourites (int): How many favourites a story has
        """
        index = 7
        if self.oneshot():
            index -= 1
        if "Words" in self.relationships() or "Chapters" in self.relationships():
            index -= 1
        return str(self.metadata[index])[6:]

    def follows(self):
        """
        Function to return how many follows a story has

        Returns:
            follows (int): How many follows a story has
        """
        index = 8
        if self.oneshot():
            index -= 1
        if "Words" in self.relationships() or "Chapters" in self.relationships():
            index -= 1
        return str(self.metadata[index])[9:]

    def lastUpdated(self):
        """
        Function to return when a story was last updated

        Returns:
            lastUpdated (datetime): When a story was last updated
        """
        index = 9
        if self.oneshot():
            index -= 1
        if "Words" in self.relationships() or "Chapters" in self.relationships():
            index -= 1
        rawHTML = self.metadata[index]
        rawDate = rawHTML.split(">")[1].split("<")[0]
        splitDate = rawDate.split("/")
        return datetime.date(day=int(splitDate[1]), month=int(splitDate[0]), year=int(splitDate[2]))

    def published(self):
        """
        Function to return when a story was published

        Returns:
            published (datetime): When a story was published
        """
        index = 10
        if self.oneshot():
            index -= 1
        if "Words" in self.relationships() or "Chapters" in self.relationships():
            index -= 1
        rawHTML = self.metadata[index]
        rawDate = rawHTML.split(">")[1].split("<")[0]
        splitDate = rawDate.split("/")
        return datetime.date(day=int(splitDate[1]), month=int(splitDate[0]), year=int(splitDate[2]))

    def status(self):
        """
        Function to return a story's status

        Returns:
            status (string): A story's status
        """
        index = 11
        if self.oneshot():
            index -= 1
        if "Words" in self.relationships() or "Chapters" in self.relationships():
            index -= 1
        return self.metadata[index][8:]

    def getChapterText(self, chapter, rate_limit=0):
        """
        Function to request a chapter's text

        Parameters:
            chapter (int): The specific chapter to get

        Raises:
            exceptions.InvalidChapterID: Invalid chapter number

        Returns:
            chapterText (array): A chapter's text
        """
        chapterText = []
        retries = 5
        if chapter < 1 or chapter > self.chapters():
            raise exceptions.InvalidChapterID(f"{chapter} is not a valid chapter")
        while True:
            try:
                if retries > 0:
                    soup = self.requester(f"https://www.fanfiction.net/s/{self.id}/{chapter}", rate_limit)
                    break
            except cloudscraper.exceptions.CloudflareChallengeError:
                retries -= 1
                continue
        textList = str(soup.find_all("div", {"class": "storytext xcontrast_txt nocopy"})).split("</p><p>")
        for text in textList:
            chapterText.append(self.cleaner(text))
        return chapterText

    def getStoryText(self):
        """
        Function to request a story's entire text

        Returns:
            storyText (2D array): A story's text
        """
        if self.oneshot():
            return self.getChapterText(1, 2)
        else:
            storyText = []
            for chapter in range(self.chapters()):
                storyText.append(self.getChapterText(chapter+1, 2))
            return storyText

    def cleaner(self, htmlString):
        """
        Function to remove all HTML tags from a string

        Parameters:
            htmlString (string): The HTML string

        Returns:
            cleanedHTML (string): The cleaned HTML string
        """
        removedBrackets = htmlString.replace("[", "").replace("]", "")
        removedHTML = re.sub(r"<.*?>", '', removedBrackets)
        return re.sub(r"\n", '', removedHTML)