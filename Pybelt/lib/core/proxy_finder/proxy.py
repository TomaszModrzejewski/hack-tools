import urllib2
import json
import time
import socket
import httplib
from lib.core.settings import PROXY_URL
from lib.core.settings import LOGGER
from lib.core.settings import PROXY_SCAN_RESULTS
from lib.core.settings import create_random_filename
from lib.core.settings import create_dir


def connect_and_pull_info():
    """ Connect to the proxy source and pull the proxies in JSON form """
    data = json.loads(urllib2.urlopen(PROXY_URL).read())
    results = {count: data[i] for count, i in enumerate(range(60), start=1)}
    LOGGER.info(
        f"Found {len(results)} possible proxies, moving to connection attempts.."
    )

    return results


def attempt_to_connect_to_proxies():
    """ Attempted connections to the proxies pulled from the JSON data """
    results = []
    prox_info = connect_and_pull_info()
    for i, proxy in enumerate(prox_info, start=1):
        if prox_info[i]["type"] == "HTTP":
            candidate = f'{prox_info[i]["type"]}://{prox_info[i]["ip"]}:{prox_info[i]["port"]}'

            opener = urllib2.build_opener(urllib2.ProxyHandler({"http": candidate}))
            urllib2.install_opener(opener)
            request = urllib2.Request("http://google.com")
            try:
                start_time = time.time()
                urllib2.urlopen(request, timeout=10)
                stop_time = time.time() - start_time
                LOGGER.info(
                    f'Successful: {candidate.lower()}\n\t\tLatency: {stop_time}s\n\t\tOrigin: {prox_info[i]["country"]}\n\t\tAnonymity: {prox_info[i]["anonymity"]}\n\t\tType: {prox_info[i]["type"]}'
                )

                results.append("http://" + prox_info[i]["ip"] + ":" + prox_info[i]["port"])
            except urllib2.HTTPError:
                pass
            except urllib2.URLError:
                pass
            except socket.timeout:
                pass
            except httplib.BadStatusLine:
                pass
            except socket.error:
                pass
    LOGGER.info(f"Found a total of {len(results)} proxies.")
    filename = create_random_filename()
    create_dir(PROXY_SCAN_RESULTS)
    with open(f"{PROXY_SCAN_RESULTS}/{filename}.txt", "a+") as res:
        for prox in results:
            res.write(prox + "\n")
    LOGGER.info(f"Results saved to: {PROXY_SCAN_RESULTS}/{filename}.txt")
