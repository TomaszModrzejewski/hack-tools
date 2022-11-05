import httplib2
import re

from lib.core import settings
from google import search
from lib.core.settings import LOGGER
from lib.core.settings import create_dir


class DorkScanner(object):

    """ Check your Google dorks to see if they actually will find sites that you want """

    def __init__(self, dork, proxy=None, dork_file=None):
        self.dork = dork
        self.proxy = proxy
        self.dorks = dork_file
        self.searchEngine = 'http://google.com'

    def configure_proxy(self):
        """ Configure a proxy so that the API accepts it, had to use httplib2.. """
        if self.proxy is None:
            return None
        prox_list = self.proxy.split(":")
        prox_list[0] = ""
        prox_list[1] = '.'.join(re.findall(r"\d+", prox_list[1]))
        return httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
                                  proxy_host=prox_list[1],
                                  proxy_port=prox_list[2])

    def connect_to_search_engine(self):
        """ Connect to Google and search for URLS """
        self.configure_proxy() if self.proxy is not None else None
        res = []
        limit = 100
        found = 0
        index = search(self.dork)
        while limit != 0:
            res.append(next(index))
            limit -= 1
            found += 1
        return res

    def check_urls_for_queries(self):
        """ The returned URLS will be run through a query regex to see if they have a query parameter
            http://google.com <- False
            http://example.com/php?id=2 <- True """
        filename = settings.create_random_filename()
        LOGGER.info(f"File being saved to: {filename}.txt")
        create_dir(settings.DORK_SCAN_RESULTS_PATH)
        with open(f"{settings.DORK_SCAN_RESULTS_PATH}/{filename}.txt", "a+") as results:
            for url in self.connect_to_search_engine():
                if match := settings.QUERY_REGEX.match(url):
                    results.write(url + "\n")
        amount_of_urls = len(
            open(
                f"{settings.DORK_SCAN_RESULTS_PATH}/{filename}.txt", 'r'
            ).readlines()
        )

        success_rate = ((amount_of_urls // 10) + 1) * 10
        return f"Found a total of {amount_of_urls} usable links with query (GET) parameters, urls have been saved to {settings.DORK_SCAN_RESULTS_PATH}/{filename}.txt. This Dork has a success rate of {success_rate}%"
