# https://github.com/FabricMC/fabric-meta#fabric-meta

from json import loads as json_loads
from typing import TypedDict
from urllib.request import urlopen

from src import console

class GameVersionInfo(TypedDict):
    version: str
    stable: bool

class LoaderVersionInfo(TypedDict):
    separator: str
    build: int
    maven: str
    version: str
    stable: bool

class InstallerVersionInfo(TypedDict):
    url: str
    maven: str
    version: str
    stable: bool

class Versions(TypedDict):
    game: list[GameVersionInfo]
    loader: list[LoaderVersionInfo]
    installer: list[InstallerVersionInfo]

class FabricData:
    __slots__ = ("versions", "game_version", "loader_version", "installer_version",)

    def __init__(self, versions: Versions, game_version: str, loader_version: str, installer_version: str):
        self.versions = versions
        self.game_version = game_version
        self.loader_version = loader_version
        self.installer_version = installer_version

def get_versions() -> Versions:
    return json_loads(urlopen("https://meta.fabricmc.net/v2/versions").read())

def download(game_version: str, loader_version: str, installer_version: str, path: str):
    jar_filename = "fabric-server-mc.%s-loader.%s-launcher.%s.jar" % (game_version, loader_version, installer_version,)
    with open(path + "/" + jar_filename, "wb") as jar:
        jar.write(urlopen("https://meta.fabricmc.net/v2/versions/loader/%s/%s/%s/server/jar" % (game_version, loader_version, installer_version,)).read())
    return jar_filename

def ask():
    versions = get_versions()

    print("\nHide unstable version? [y, n]: ")
    if console.ask_yes_no():
        game_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"], versions["game"])))
    else:
        game_versions = tuple(map(lambda x: x["version"], versions["game"]))
    print("\nVersion (Default: Latest):")
    selected_game_version = game_versions[console.ask_iterable(game_versions, 1) - 1]

    loader_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"], versions["loader"])))
    print("\nFabric Loader Version (Default: Latest):")
    selected_loader_version = loader_versions[console.ask_iterable(loader_versions) - 1]

    selected_installer_version = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"], versions["installer"])))[0]

    return FabricData(versions, selected_game_version, selected_loader_version, selected_installer_version,)

def create_server(game_version: str, loader_version: str, installer_version: str, path: str, xmx: int, xms: int = -1):
    jar_filename = download(game_version, loader_version, installer_version, path)
    with open(path + "/run.bat", "w") as bat:
        content = "@echo off\njava"
        if xms != -1:
            content += " -Xms%dG" % xms
        content += " -Xmx%dG -jar %s nogui\npause" % (xmx, jar_filename,)
        bat.write(content)

def show_server_info(data: FabricData):
    print("Software: Fabric\nGame Version: %s\nLoader Version: %s\nInstaller Version: %s\n" % (data.game_version, data.loader_version, data.installer_version,))