from urllib import request
from bs4 import BeautifulSoup
from ratelimiter import RateLimiter
from tqdm import tqdm


class WebScraper:

    def __init__(self, webSite):
        # the website homepage URL that we want to scrape
        self.websiteURL = website
        # the initialization of the two parameter to set the RateLimiter
        # for hitting websites is very cautious. It can be sequently
        # changed using the "setRateLimiter" method
        self.max_calls = 1
        self.period = 1

    # This function is needed to set the ratelimiter to hit the website
    def setRateLimiter(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period

    # this function return the html file at @url as a string
    @RateLimiter(max_calls=self.max_calls, period=self.period)
    def downloadURL(self, url, opener):
        try:
            f = opener.open(url)
            return f.read()
        except:
            print(url)

    # if the link don't start with the websiteURL add it at the beginning
    # otherwise you will return as it is.
    def _buildLink(self, link, websiteURL):
        if link.startswith(websiteURL):
            return link
        else:
            return websiteURL + link

    # given an html string and the index of the advertisement, this function
    # writes all on the filesystem
    def _writeHtml(self, html, ad_index):
        # save the description on a textfile
        with open("./htmls/htmlAd#" + str(ad_index) + ".txt", "w") as text_file:
            text_file.write(html)

    # In this implementation the html parser is instatiated using the BeautifulSoup library
    def _createHtmlParser(self, webPageHtml):
        return (BeautifulSoup(webPageHtml, 'html.parser'))

    # In this implementation each ad is contained in a html <p> tag with an attribute 'class'
    # with a name equal to "titolo text-primary"
    def _retrieveListOfAds(self, htmlParser):
        return (htmlParser.find_all('p', attrs={"class": "titolo text-primary"}))

    # In this implementation given the html tag that contains the info about an advertisement
    # it is possible to get the URL that points to the advertisement
    def _getAdLink(self, adTag):
        return (adTag.find('a').get('href'))

    # This function is used to download the html file of all the house advertisements
    # The input paramaters are the following:
    # Total number of webpages containing the house ads to download
    # NUMBER_OF_WEBPAGES = 1500
    # Number of house ads to download
    # NUMBER_OF_ADS = 15000
    # starting webpage at which the house ads list can be downloaded
    # startingwebpage = 495
    # variable used to index the html stored on the filesystem
    # ad_index = 4599
    # variable which counts how many webpages have been downloaded
    # count_webpages = 1
    # the base URL where all the house ads collection is contained
    # baseURL = "https://www.immobiliare.it/vendita-case/roma/?criterio=rilevanza&pag="
    def downloadAllAds(self, ad_index, NUMBER_OF_WEBPAGES, NUMBER_OF_ADS, startingwebpage, baseURL):
        # This function have been used with the following parameters:
        # ad_index: 495
        # NUMBER_OF_WEBPAGES = 1500
        # NUMBER_OF_ADS = 15000
        # startingwebpage = 495
        # baseURL = "https://www.immobiliare.it/vendita-case/roma/?criterio=rilevanza&pag="
        # instatiate the object needed to download the html file given a specific URL
        opener = request.FancyURLopener({})
        # for each webpage downloaded
        for webpageId in tqdm(range(startingwebpage, NUMBER_OF_WEBPAGES + 1)):
            # download the page at https://www.immobiliare.it/vendita-case/roma/?criterio=rilevanza&pag=[webpageId]
            webPageHtml = self._downloadURL(url=baseURL + str(webpageId), opener=opener)
            # create the html parser using the library BeautifulSoup
            htmlParser = self._createHtmlParser(webPageHtml=webPageHtml)
            # retrieve all the ads
            allAds = self._retrieveListOfAds(htmlParser=htmlParser)
            # Retrieve all the links pointing to the single house ad which are contained inside the html page
            allLinks = [buildLink(link=self._getAdLink(adTag=ad), websiteURL=self.websiteURL) for ad in allAds]
            # for each link which points to the house ad
            for linkAd in allLinks:
                # increase the index of the ad
                ad_index += 1
                # download the html file of the advertisement webpage
                htmlFile = downloadURL(url=linkAd, opener=opener)
                # create the html parser using the library BeautifulSoup
                soup = self._createHtmlParser(webPageHtml=htmlFile)
                # write the html
                self._writeHtml(html=soup.prettify(), ad_index=ad_index)
                # update the counter
                count_webpages += 1
                # if the number of webpages downloaded exceed the number of ads
                # requested as input, then the procedure is early stopped
                if (count_webpages >= NUMBER_OF_ADS):
                    print("[LOG]:All the necessary webpages have been downloaded")
                    return
        print("[LOG]: " + str(count_webpages) + " webpages have been downloaded")