from http.client import HTTPConnection
from os.path import exists

from orjson import loads as json_loads

def request(connection: HTTPConnection, url: str):
    connection.request("GET", url)
    return json_loads(connection.getresponse().read())

def request_download(connection: HTTPConnection, url: str, filepath: str):
    if not exists(filepath):
        connection.request("GET", url)
        with open(filepath, "wb") as f:
            f.write(connection.getresponse().read())

def url_domain(url: str):
    return url[url.index("://", 5) + 3:url.index("/", url.index("://", 5) + 3)]

def url_path(url: str):
    return url[url.index("/", url.index("://", 5) + 3):]