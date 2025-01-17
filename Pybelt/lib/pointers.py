import re
import urllib2
import socket
import subprocess
from urllib2 import HTTPError
from requests.exceptions import ConnectionError

# Libraries
from lib.core.dork_check import DorkScanner
from lib.core.errors import GoogleBlockException
from lib.core.hash_cracking import HashCracker
from lib.core.hash_cracking.hash_checker import HashChecker
from lib.core.port_scan import PortScanner
from lib.core.proxy_finder import attempt_to_connect_to_proxies
from lib.core.sql_scan.xss_scan import xss
from lib.core.sql_scan import SQLiScanner

# Settings
from lib.core.settings import GOOGLE_TEMP_BLOCK_ERROR_MESSAGE
from lib.core.settings import IP_ADDRESS_REGEX
from lib.core.settings import LOGGER
from lib.core.settings import QUERY_REGEX
from lib.core.settings import URL_REGEX
from lib.core.settings import RANDOM_USER_AGENT
from lib.core.settings import prompt
from lib.core.settings import replace_http


def run_sqli_scan(url, url_file=None, proxy=None, user_agent=False, tamper=None):
    """ Pointer to run a SQLi Scan on a given URL """
    error_message = "URL: '{}' threw an exception {} "
    error_message += "and Pybelt is unable to resolve the URL, "
    error_message += "this could mean that the URL is not allowing connections "
    error_message += "or that the URL is bad. Attempt to connect "
    error_message += "to the URL manually, if a connection occurs "
    error_message += "make an issue."
    if url_file is not None:  # Run through a file list
        file_path = url_file
        done = 0
        try:
            total = len(open(file_path).readlines())
            LOGGER.info("Found a total of {} urls in file {}..".format(total, file_path))
            with open(file_path) as urls:
                for url in urls.readlines():
                        if QUERY_REGEX.match(url.strip()):
                            question = prompt("Would you like to scan '{}' for SQLi vulnerabilities[y/N]: ".format(
                                url.strip()
                            ))
                            if question.lower().startswith("y"):
                                LOGGER.info("Starting scan on url: '{}'".format(url.strip()))
                                try:
                                    LOGGER.info(SQLiScanner(url.strip()).sqli_search())
                                    done += 1
                                    LOGGER.info("URLS scanned: {}, URLS left: {}".format(done, total - done))
                                except urllib2.URLError:
                                    done += 1
                                    LOGGER.warning("{} did not respond, skipping..".format(url.strip()))
                            else:
                                done += 1
                                pass
                        else:
                            done += 1
                            LOGGER.warn("URL '{}' does not contain a query (GET) parameter, skipping..".format(url.strip()))
                            pass
            LOGGER.info("No more URLS found in file, shutting down..")
        except HTTPError as e:
            LOGGER.fatal(error_message.format(url.strip(), e))
        except IOError as e:
            print e
            LOGGER.fatal("That file does not exist, verify path and try again.")

    else:  # Run a single URL
        try:
            if QUERY_REGEX.match(url):
                LOGGER.info("Starting SQLi scan on '{}'..".format(url))
                LOGGER.info(SQLiScanner(url).sqli_search())
            else:
                LOGGER.error("URL does not contain a query (GET) parameter. Example: http://example.com/php?id=2")
        except HTTPError as e:
            LOGGER.fatal(error_message.format(url, e))


def run_xss_scan(url, url_file=None, proxy=None, user_agent=False):
    """ Pointer to run a XSS Scan on a given URL """
    proxy = proxy if proxy is not None else None
    header = RANDOM_USER_AGENT if user_agent is not False else None
    if proxy is not None:
        LOGGER.info(f"Proxy configured, running through: {proxy}")
    if user_agent is True:
        LOGGER.info(f"Grabbed random user agent: {header}")

    if url_file is not None:  # Scan a given file full of URLS
        file_path = url_file
        done = 0
        try:
            total = len(open(url_file).readlines())
            LOGGER.info(f"Found a total of {total} URLS to scan..")
            with open(file_path) as urls:
                for url in urls:
                    if QUERY_REGEX.match(url.strip()):
                        question = prompt(
                            f"Would you like to scan '{url.strip()}' for XSS vulnerabilities[y/N]: "
                        )

                        done += 1

                        if question.lower().startswith("y"):
                            try:
                                if xss.main(url.strip(), proxy=proxy, headers=header):
                                    LOGGER.info(f"URL '{url.strip()}' appears to be vulnerable to XSS")
                                else:
                                    LOGGER.info(f"URL '{url.strip()}' does not appear to be vulnerable to XSS")
                            except ConnectionError:
                                LOGGER.warning(f"{url.strip()} failed to respond, skipping..")

                            LOGGER.info(f"URLS scanned: {done}, URLS left: {total - done}")
                    else:
                        done += 1
                        LOGGER.warn(
                            f"URL '{url.strip()}' does not contain a query (GET) parameter, skipping.."
                        )

            LOGGER.info("All URLS in file have been scanned, shutting down..")
        except IOError:
            LOGGER.fatal("That file does not exist, verify path and try again.")

    elif QUERY_REGEX.match(url):
        LOGGER.info("Searching: {} for XSS vulnerabilities..".format(url, proxy=proxy, headers=header))
        if not xss.main(url, proxy=proxy, headers=header):
            LOGGER.error(f"{url} does not appear to be vulnerable to XSS")
        else:
            LOGGER.info(f"{url} seems to be vulnerable to XSS.")
    else:
        error_message = (
            "The URL you provided does not contain a query "
            + "(GET) parameter. In order for this scan you run "
        )

        error_message += "successfully you will need to provide a URL with "
        error_message += "A query (GET) parameter example: http://127.0.0.1/php?id=2"
        LOGGER.fatal(error_message)


def run_port_scan(host):
    """ Pointer to run a Port Scan on a given host """
    if re.search(IP_ADDRESS_REGEX, host) is not None:
        LOGGER.info(f"Starting port scan on IP: {host}")
        PortScanner(host).connect_to_host()
    elif re.search(URL_REGEX, host) is not None and re.search(QUERY_REGEX, host) is None:
        try:
            LOGGER.info("Fetching resolve IP...")
            ip_address = socket.gethostbyname(replace_http(host))
            LOGGER.info(f"Done! IP: {ip_address}")
            LOGGER.info(f"Starting scan on URL: {host} IP: {ip_address}")
            PortScanner(ip_address).connect_to_host()
        except socket.gaierror:
            error_message = f"Unable to resolve IP address from {host}. You can manually get the IP address and try again,"

            error_message += " dropping the query parameter in the URL (IE php?id=),"
            error_message += " or dropping the http or https"
            error_message += " and adding www in place of it. IE www.google.com"
            error_message += " may fix this issue."
            LOGGER.fatal(error_message)
    else:
        error_message = (
            "You need to provide a host to scan,"
            + " this can be given in the form of a URL "
        )

        error_message += "or a IP address. Dropping the query (GET) "
        error_message += "of the URL may resolve this problem, or "
        error_message += "verify that the IP is real"
        LOGGER.fatal(error_message)


def run_hash_cracker(hash_to_crack, hash_file=None):
    """ Pointer to run the Hash Cracking system """
    try:
        items = list(''.join(hash_to_crack).split(":"))
        if items[1] == "all":
            LOGGER.info("Starting hash cracking without knowledge of algorithm...")
            HashCracker(items[0]).try_all_algorithms()
        else:
            LOGGER.info(f"Starting hash cracking using {items[1]} as algorithm type..")
            HashCracker(items[0], type=items[1]).try_certain_algorithm()
    except IndexError:
        error_message = (
            "You must specify a hash type in order for this to work. "
            + "Example: 'python pybelt.py -c 098f6bcd4621d373cade4e832627b4f6:md5'"
        )

        LOGGER.fatal(error_message)


def run_hash_verification(hash_to_verify, hash_ver_file=None):
    """ Pointer to run the Hash Verification system"""
    if hash_ver_file is not None and hash_to_verify is None:
        try:
            total = len(open(hash_ver_file).readlines())
            LOGGER.info(f"Found a total of {total} hashes in file..")
        except IOError:
            LOGGER.critical("That file does not exist, check path and try again.")

        with open(hash_ver_file, "r+") as hashes:
            for h in hashes:
                question = prompt(f"Attempt to verify '{h.strip()}'[y/N]: ")
                if question.startswith("y"):
                    LOGGER.info(f"Analyzing hash: '{h.strip()}'")
                    HashChecker(h.strip()).obtain_hash_type()
                    print("\n")
                else:
                    LOGGER.warning(f"Skipping '{h.strip()}'..")
    else:
        LOGGER.info(f"Analyzing hash: '{hash_to_verify}'")
        HashChecker(hash_to_verify).obtain_hash_type()


def run_dork_checker(dork, dork_file=None, proxy=None):
    """ Pointer to run a Dork Check on a given Google Dork """
    if dork is not None:
        LOGGER.info(f"Starting dork scan, using query: '{dork}'..")
        try:
            LOGGER.info(DorkScanner(dork, dork_file=dork_file, proxy=proxy).check_urls_for_queries())
        except HTTPError:
            LOGGER.fatal(GoogleBlockException(GOOGLE_TEMP_BLOCK_ERROR_MESSAGE))
    elif dork_file is not None:
        if proxy is None:
            proxy_warn = (
                "It is advised to use proxies while running "
                + "a dork list due to the temporary Google "
            )

            proxy_warn += "bans.."
            LOGGER.warning(proxy_warn)
            question = prompt("Would you like to find proxies with the built in finder first[y/N]: ")
            if question.upper().startswith("Y"):
                subprocess.call(["python", "pybelt.py", "-f"])
        try:
            with open(f"{dork_file}") as dork_list:
                for dork in dork_list:
                    LOGGER.info(f"Starting dork scan on {dork.strip()}..")
                    LOGGER.info(DorkScanner(dork, dork_file=dork_file, proxy=proxy).check_urls_for_queries())
        except HTTPError:
            LOGGER.fatal(GoogleBlockException(GOOGLE_TEMP_BLOCK_ERROR_MESSAGE))
        except IOError:
            LOGGER.fatal(
                f"The filename {dork_file} does not exist, please verify path and try again"
            )


def run_proxy_finder():
    """ Pointer to run Proxy Finder """
    LOGGER.info("Starting proxy search..")
    attempt_to_connect_to_proxies()