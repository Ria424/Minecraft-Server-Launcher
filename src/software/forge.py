from urllib.request import urlopen

from bs4 import BeautifulSoup, Tag

soup = BeautifulSoup(urlopen("https://files.minecraftforge.net/net/minecraftforge/forge/index.html"), "html.parser")
ahh = soup.select_one("body > main > div.sidebar-left.sidebar-sticky > aside > section > ul").find_all("li")
for a in ahh:
    a: Tag
    for b in a.select("ul > li"):
        if (c := b.find("a")) is not None:
            print(c.get_text())

# TODO 각 버전의 포지 로더 버전 구하기