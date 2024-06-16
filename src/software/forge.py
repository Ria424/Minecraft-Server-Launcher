# https://files.minecraftforge.net/net/minecraftforge/forge

from argparse import Namespace
from datetime import datetime
from http.client import HTTPSConnection
from os.path import join as path_join
from subprocess import Popen
from typing import OrderedDict

from bs4 import BeautifulSoup, SoupStrainer

from src import console, server
from src.minecraft_version import get_minimum, to_vanilla_format
from src.software import vanilla
from src.util import constants, request_download, url_path

ForgeVersions = tuple[OrderedDict[str, str], str | None]

def connect():
    return HTTPSConnection(constants.FORGE_FILES_DOMAIN)

def connect_maven():
    return HTTPSConnection(constants.FORGE_MAVEN_DOMAIN)

def get_versions(connection: HTTPSConnection, game_version: str, version_type: str):
    download_list_only = SoupStrainer("table", {"class": "download-list"})
    connection.request("GET", f"/net/minecraftforge/forge/index_{game_version}.html")
    soup = BeautifulSoup(connection.getresponse().read(), "html.parser", parse_only=download_list_only)
    return get_versions_base(soup, version_type)

def get_versions_base(soup: BeautifulSoup, version_type: str) -> ForgeVersions:
    versions: OrderedDict[str, str] = OrderedDict()
    recommended_version: str | None = None

    for tag_tr in soup.select("tbody > tr"):
        version_tag = tag_tr.find("td", {"class": "download-version"}, recursive=False)
        version = version_tag.get_text(strip=True)
        if version_tag.find("i", {"class": "promo-recommended"}, recursive=False) is not None:
            recommended_version = version
        for tag_li in tag_tr.select("td.download-files > ul > li"):
            label = tag_li.find("a", recursive=False).get_text(strip=True)
            if label.lower() == version_type.lower():
                tag_a = tag_li.find("a", {"class": ("info-link", "tooltipstered",)}, recursive=False)
                if tag_a is not None and tag_a.has_attr("href"):
                    versions[version] = tag_a.attrs["href"]

    return versions, recommended_version

def get_game_versions(connection: HTTPSConnection):
    versions: list[str] = []

    sidebar_only = SoupStrainer("section", {"class": "sidebar-nav"})
    connection.request("GET", "/net/minecraftforge/forge/index.html")
    soup = BeautifulSoup(connection.getresponse().read(), "html.parser", parse_only=sidebar_only)
    for tag_li in soup.select("ul > li > ul > li"):
        version = tag_li.get_text(strip=True)
        if constants.FORGE_FIRST_INSTALLER_SUPPORT == version or get_minimum(constants.FORGE_FIRST_INSTALLER_SUPPORT, version) != version:
            versions.append(version)

    return versions

def download(connection: HTTPSConnection, url: str, path: str):
    installer_jar = url[url.rindex("/") + 1:]
    request_download(connection, url_path(url), path_join(path, installer_jar))
    return installer_jar

def install(installer: str, path: str):
    if Popen(f"java -jar {installer} --installServer", cwd=path).wait() < 0:
        raise

# 1.17.1+
def edit_jvm_args(path: str, args: str):
    with open(path_join(path, "user_jvm_args.txt"), "a") as f:
        f.write(f"\n{args}")

def cli(args: Namespace, path: str):
    console.print("\rGathering required information...")
    connection = connect()

    game_versions = get_game_versions(connection)
    selected_game_version_index = game_versions.index(args.game_version) if args.game_version is not None else 0
    selected_game_version = game_versions[selected_game_version_index]

    loader_version_urls, recommended = get_versions(connection, selected_game_version, "Installer")
    connection.close()

    loader_versions = tuple(loader_version_urls)

    default_loader_version_index = 0
    if recommended is not None:
        default_loader_version_index = loader_versions.index(recommended)

    selected_loader_version_index = loader_versions.index(args.game_version) if args.forge_loader_version is not None else default_loader_version_index
    _, download_url = tuple(loader_version_urls.items())[selected_loader_version_index]

    xmx = args.xmx
    xms = args.xms or xmx
    # server.show_server_info(f"Software: Forge\nGame Version: {selected_game_version}\nLoader Version: {selected_loader_version}\n", xms, xmx)
    console.print(" Done\n")

    console.print("\rDownloading server jar file...")
    connection_maven = connect_maven()
    installer_jar = download(connection_maven, download_url, path)
    connection_maven.close()
    console.print(" Done\n")

    console.print("\rInstalling server...\n")
    install(installer_jar, path)
    console.print("\rInstalling server... Done\n")

    console.print("\rWriting batch file...")

    vanilla_format_version = to_vanilla_format(selected_game_version)

    nogui = True
    if int(selected_game_version.split(".", 2)[1]) >= 17:
        edit_jvm_args(path, f"{server.jvm_args.xms(xms) if xms > 0 else ""} {server.jvm_args.xmx(xmx)}")
        if nogui:
            batch_path = path_join(path, "run.bat")
            with open(batch_path, "r") as bat:
                content = bat.read().replace("%*", "%* nogui")
            with open(batch_path, "w") as bat:
                bat.write(content)
    else:
        server.write_batch(path, xms, xmx, f"minecraft_server.{vanilla_format_version}.jar", True)

    console.print(" Done\n")

    if args.agree_eula:
        vanilla_connection = vanilla.connect()
        manifest = vanilla.get_version_manifest(vanilla_connection)
        vanilla_connection.close()
        selected_game_version_released = tuple(filter(lambda x: x["id"] == vanilla_format_version, manifest["versions"]))[0]["releaseTime"]
        if server.is_need_eula(datetime.fromisoformat(selected_game_version_released)):
            server.write_eula(path)

    if args.launch:
        server.launch(path)