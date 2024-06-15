from contextlib import closing
from http.client import HTTPConnection, HTTPSConnection
from json import loads as json_loads
from os.path import exists

# class HTTPSConnectionWith(HTTPSConnection):
#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.close()

def connect_with(host: str):
    return closing(HTTPSConnection(host))

def request(connection: HTTPConnection, url: str):
    connection.request("GET", url)
    return json_loads(connection.getresponse().read())

def request_download(connection: HTTPSConnection, url: str, filepath: str):
    if not exists(filepath):
        connection.request("GET", url)
        with open(filepath, "wb") as f:
            f.write(connection.getresponse().read())

def url_domain(url: str):
    return url[url.index("://", 5) + 3:url.index("/", url.index("://", 5) + 3)]

def url_path(url: str):
    return url[url.index("/", url.index("://", 5) + 3):]