from . import utils
import cloudscraper
from bs4 import BeautifulSoup
import datetime
import time
import re


class Story:
    def __init__(self, link, rate_limit=0, loaded=True):
        self._soup = None
        self._rate_limit = rate_limit
        self._loaded = False
        self._scraper = cloudscraper.CloudScraper(browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False,
            "desktop": True
        })
        self._id = self.getID(link)
        self._link = f"https://www.fanfiction.net/s/{self._id}"
        self._metadata = None
        if loaded:
            self.update()

    def __repr__(self):
        return f"<Story({self._id})>"


    def update(self):
        """
        Function to update the metadata and soup for a story
        """
        soup = self._requester(self._link, self._rate_limit)
        metadataRaw = soup.find("span", {"class": "xgray xcontrast_txt"})
        self._metadata = self._metadataAssign(str(metadataRaw).split(" - "))
        self._soup = soup
        self._loaded = True


    def _requester(self, link, rate_limit):
        """
        Function to request a story's webpage

        Parameters:
            link (str): The link to be requested
            rate_limit (int): How long between each request

        Raises:
            exceptions.FFInvalidStoryLink: Invalid story url
            cloudscraper.exceptions.CloudflareChallengeError: Cloudflare version 2 challenge

        Returns:
            tempSoup (BeautifulSoup object): The story's webpage
        """
        if self._id == None:
            raise utils.FFInvalidLink("Link is invalid")
        else:
            time.sleep(rate_limit)
            try:
                request = self._scraper.get(link)
            except cloudscraper.exceptions.CloudflareChallengeError:
                raise utils.CloudflareError("A Cloudflare version 2 check has been detected. Please try again in a little while")
            tempSoup = BeautifulSoup(request.text, features="lxml")
            invalidStory = tempSoup.find("span", {"class": "gui_warning"})
            if invalidStory != None:
                raise utils.FFInvalidLink("Link is invalid")
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

    def _metadataAssign(self, details):
        final = {
            "rating": None,
            "language": None,
            "genre": None,
            "relationships": None,
            "chapters": None,
            "words": None,
            "favourites": None,
            "follows": None,
            "lastUpdated": None,
            "published": None,
            "status": None
        }
        for count in range(len(details)):
            if "rating" in details[count]:
                final["rating"] = BeautifulSoup(details[count], features="lxml").find("a").text
            elif "Chapters" in details[count]:
                final["chapters"] = int(details[count][9:])
            elif "Words" in details[count]:
                final["words"] = int(details[count][7:].replace(",", ""))
            elif "Favs" in details[count]:
                final["favourites"] = int(details[count][6:].replace(",", ""))
            elif "Follows" in details[count]:
                final["follows"] = int(details[count][9:].replace(",", ""))
            elif "Updated" in details[count]:
                timestamp = details[count].split('"')[1]
                final["lastUpdated"] = datetime.date.fromtimestamp(int(timestamp))
            elif "Published" in details[count]:
                timestamp = details[count].split('"')[1]
                final["published"] = datetime.date.fromtimestamp(int(timestamp))
            elif "Status" in details[count]:
                final["status"] = details[count][8:]
        final["language"] = details[1]
        final["genre"] = details[2]
        if final["chapters"] == None:
            final["chapters"] = 1
        if not ("Chapters" in details[3] or "Words" in details[3]):
            final["relationships"] = details[3]
        return final

    def oneshot(self):
        """
        Function to return if a story is a oneshot or not

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            oneshot (boolean): True if the story is a oneshot or false if it is not
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        request = self._requester(f"https://www.fanfiction.net/s/{self._id}/2", 0)
        try:
            oneshotTest = request.find("span", {"class": "gui_normal"}).text
            return True
        except AttributeError:
            return False

    def title(self):
        """
        Function to return a story's title

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            title (string): A story's title
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._soup.find("b", {"class": "xcontrast_txt"}).text

    def authors(self):
        """
        Function to return a story's authors

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            authors (string): The story's authors
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        hrefList = self._soup.find_all("a", {"class": "xcontrast_txt"})
        if "/u/" in str(hrefList[1]):
            href = hrefList[1]["href"].replace("-", " ")
        else:
            href = hrefList[2]["href"].replace("-", " ")
        return f"https://www.fanfiction.net{href}"

    def fandoms(self):
        """
        Function to return a story's fandom

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            fandom (string): The story's fandom
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._soup.find_all("a", {"class": "xcontrast_txt"})[1].text

    def rating(self):
        """
        Function to return a story's rating

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            rating (string): A story's rating
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["rating"]

    def language(self):
        """
        Function to return a story's language

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            language (string): A story's language
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["language"]

    def genre(self):
        """
        Function to return a story's genre

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            genre (string): A story's genre
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["genre"]

    def relationships(self):
        """
        Function to return a story's relationships

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            relationships (string): A story's relationships
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["relationships"]

    def chapters(self):
        """
        Function to return a story's chapter count

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            chapters (int): A story's chapter count
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["chapters"]

    def words(self):
        """
        Function to return a story's word count

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            words (int): A story's word count
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["words"]

    def reviews(self, chapter=0):
        """
        Function to return a story's reviews

        Parameters:
            chapter (int): The specific chapter to get reviews from. Default is 0 (every chapter)

        Raises:
            exceptions.InvalidChapterID: Invalid chapter number
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            reviews (2D array): A story's reviews. Each individual array is in the format:
                [Username, chapter number, date, review text]
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        if chapter < 0 or chapter > self.chapters():
            raise utils.InvalidChapterID(f"{chapter} is not a valid chapter")
        reviewFinal = []
        retries = 5
        reviews = self._requester(f"https://www.fanfiction.net/r/{self._id}/{chapter}/", 0)
        try:
            maxPage = int(reviews.find_all("a")[121]["href"].split("/")[4])
        except IndexError:
            maxPage = 1
        for page in range(maxPage):
            if page > 0:
                try:
                    if retries > 0:
                        reviews = self._requester(f"https://www.fanfiction.net/r/{self._id}/{chapter}/{page}", 2)
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
                        [self._cleaner(soup.find("div").text)]
                    ]
                    reviewFinal.append(result)
        return reviewFinal

    def favourites(self):
        """
        Function to return how many favourites a story has

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            favourites (int): How many favourites a story has
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["favourites"]

    def follows(self):
        """
        Function to return how many follows a story has

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            follows (int): How many follows a story has
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["follows"]

    def lastUpdated(self):
        """
        Function to return when a story was last updated

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            lastUpdated (datetime): When a story was last updated
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["lastUpdated"]

    def published(self):
        """
        Function to return when a story was published

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            published (datetime): When a story was published
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["published"]

    def status(self):
        """
        Function to return a story's status

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            status (string): A story's status
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        return self._metadata["status"]

    def getChapterText(self, chapter, rate_limit=0):
        """
        Function to request a chapter's text

        Parameters:
            chapter (int): The specific chapter to get

        Raises:
            exceptions.InvalidChapterID: Invalid chapter number
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            chapterText (array): A chapter's text
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        chapterText = []
        retries = 5
        if chapter < 1 or chapter > self.chapters():
            raise utils.InvalidChapterID(f"{chapter} is not a valid chapter")
        while True:
            try:
                if retries > 0:
                    soup = self._requester(f"https://www.fanfiction.net/s/{self._}/{chapter}", rate_limit)
                    break
            except cloudscraper.exceptions.CloudflareChallengeError:
                retries -= 1
                continue
        textList = str(soup.find_all("div", {"class": "storytext xcontrast_txt nocopy"})).split("</p><p>")
        for text in textList:
            chapterText.append(self._cleaner(text))
        return chapterText

    def getStoryText(self):
        """
        Function to request a story's entire text

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            storyText (2D array): A story's text
        """
        if not self._loaded:
            raise utils.WorkNotLoaded("Story is not loaded. Call story.update()")

        if self.oneshot():
            return self.getChapterText(1, 2)
        else:
            storyText = []
            for chapter in range(self.chapters()):
                storyText.append(self.getChapterText(chapter+1, 2))
            return storyText

    def _cleaner(self, htmlString):
        """
        Function to remove all HTML tags from a string

        Parameters:
            htmlString (string): The HTML string

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            cleanedHTML (string): The cleaned HTML string
        """
        removedBrackets = htmlString.replace("[", "").replace("]", "")
        removedHTML = re.sub(r"<.*?>", '', removedBrackets)
        return re.sub(r"\n", '', removedHTML)

    def getLink(self):
        """
        Function to return a story's url

        Raises:
            exceptions.WorkNotLoaded: Work is not loaded

        Returns:
            link (str): A story's url
        """
        return self._link