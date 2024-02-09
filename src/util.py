def url_path(url: str):
    return url[url.index("/", url.index("//") + 2):]