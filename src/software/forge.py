# https://files.minecraftforge.net/net/minecraftforge/forge

from dataclasses import dataclass
from datetime import datetime
from http.client import HTTPSConnection
from os import system
from subprocess import Popen

from bs4 import BeautifulSoup, SoupStrainer

from src import console, server
from src.minecraft_version import get_minimum, to_vanilla_format
from src.software import vanilla
from src.util import url_path

FIRST_INSTALLER_SUPPORT = "1.5.2"

@dataclass(repr=False, eq=False, slots=True)
class ForgeData:
    game_version: str
    version: str
    url: str

    def __repr__(self):
        return f"Software: Forge\nGame Version: {self.game_version}\nLoader Version: {self.version}\n"

def connect():
    return HTTPSConnection("files.minecraftforge.net")

def connect_maven():
    return HTTPSConnection("maven.minecraftforge.net")

def get_versions(connection: HTTPSConnection, game_version: str):
    versions: list[tuple[str, str]] = []
    recommended_version: str | None = None

    download_list_only = SoupStrainer("table", {"class": "download-list"})
    connection.request("GET", f"/net/minecraftforge/forge/index_{game_version}.html")
    soup = BeautifulSoup(connection.getresponse().read(), "html.parser", parse_only=download_list_only)
    for tag_tr in soup.select("tbody > tr"):
        version_tag = tag_tr.find("td", {"class": "download-version"}, recursive=False)
        version = version_tag.get_text(strip=True)
        if version_tag.find("i", {"class": "promo-recommended"}, recursive=False) is not None:
            recommended_version = version
        for tag_li in tag_tr.select("td.download-files > ul > li"):
            label = tag_li.find("a", recursive=False).get_text(strip=True)
            if label == "Installer":
                tag_a = tag_li.find("a", {"class": ("info-link", "tooltipstered",)}, recursive=False)
                if tag_a is not None and tag_a.has_attr("href"):
                    versions.append((version, tag_a.attrs["href"],))

    return versions, recommended_version

def get_game_versions(connection: HTTPSConnection):
    versions: list[str] = []

    sidebar_only = SoupStrainer("section", {"class": "sidebar-nav"})
    connection.request("GET", "/net/minecraftforge/forge/index.html")
    soup = BeautifulSoup(connection.getresponse().read(), "html.parser", parse_only=sidebar_only)
    for tag_li in soup.select("ul > li > ul > li"):
        version = tag_li.get_text(strip=True)
        if FIRST_INSTALLER_SUPPORT == version or get_minimum(FIRST_INSTALLER_SUPPORT, version) != version:
            versions.append(version)

    return versions

def download(connection: HTTPSConnection, url: str, path: str):
    installer_jar = url[url.rindex("/") + 1:]
    with open(f"{path}/{installer_jar}", "wb") as jar:
        connection.request("GET", url_path(url))
        jar.write(connection.getresponse().read())
    return installer_jar

def install(installer: str, path: str):
    if Popen(f"java -jar {installer} --installServer", cwd=path).wait() < 0:
        raise

# 1.17.1+
def edit_jvm_args(path: str, args: str):
    file_name = f"{path}/user_jvm_args.txt"
    with open(file_name, "a") as f:
        f.write(f"\n{args}")

def cli():
    connection = connect()
    game_versions = get_game_versions(connection)

    console.print("\nGame Version (Default: Latest):\n")
    selected_game_version = console.get_response_sequence(game_versions, 1)

    loader_versions_and_urls, recommended = get_versions(connection, selected_game_version)
    connection.close()

    loader_versions = tuple(map(lambda x: x[0], loader_versions_and_urls))

    def get_text(i: int, element: str):
        text = "[%d] %s"
        if i == 1:
            text += " (Latest)"
        if element == recommended:
            text += " (Recommended)"
        return f"{text}\n"

    if recommended is not None:
        default_version_index = loader_versions.index(recommended)
        console.print("\nLoader Version (Default: Recommended):\n")
    else:
        default_version_index = 0
        console.print("\nLoader Version (Default: Latest):\n")

    selected_version_index = console.get_response_iterable(loader_versions, default_version_index + 1, get_text) - 1

    data = ForgeData(selected_game_version, *loader_versions_and_urls[selected_version_index])

    xms, xmx = server.ask_memory()
    server.show_server_info(repr(data), xms, xmx)
    path = server.ask_server_path()

    maven_connection = connect_maven()
    installer_jar = download(maven_connection, data.url, path)
    maven_connection.close()

    system("cls")
    install(installer_jar, path)

    nogui = True
    if int(data.game_version.split(".", 2)[1]) >= 17:
        edit_jvm_args(path, server.jvm_args.xms(xms) + server.jvm_args.xmx(xmx))
        if nogui:
            with open(f"{path}/run.bat") as bat:
                content = bat.read().replace("%*", "%* nogui")
            with open(f"{path}/run.bat", "w") as bat:
                bat.write(content)
    else:
        server.write_run_batch(path, xms, xmx, f"minecraft_server.{data.game_version.replace("_pre", "-pre")}.jar", True)

    # Check if version needs EULA
    vanilla_connection = vanilla.connect()
    manifest = vanilla.get_version_manifest(vanilla_connection)
    vanilla_connection.close()
    selected_game_version_released = tuple(filter(lambda x: x["id"] == to_vanilla_format(selected_game_version), manifest["versions"]))[0]["releaseTime"]
    server.launch_server(path, datetime.fromisoformat(selected_game_version_released))
