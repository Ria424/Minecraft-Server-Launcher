# https://github.com/FabricMC/fabric-meta#fabric-meta

from http.client import HTTPSConnection
from json import loads as json_loads
from typing import TypedDict

from src import console, server
from src.util import constants

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

def connect():
    return HTTPSConnection(constants.FABRIC_API_DOMAIN)

def get_versions(connection: HTTPSConnection) -> Versions:
    connection.request("GET", "/v2/versions")
    return json_loads(connection.getresponse().read())

def get_jar_filename(game_version: str, loader_version: str, installer_version: str):
    return f"fabric-server-mc.{game_version}-loader.{loader_version}-launcher.{installer_version}.jar"

def download(connection: HTTPSConnection, game_version: str, loader_version: str, installer_version: str, path: str):
    jar_filename = get_jar_filename(game_version, loader_version, installer_version)
    connection.request("GET", f"/v2/versions/loader/{game_version}/{loader_version}/{installer_version}/server/jar")
    with open(path + "/" + jar_filename, "wb") as jar:
        jar.write(connection.getresponse().read())
    return jar_filename

def cli():
    connection = connect()
    versions = get_versions(connection)

    console.print("\nHide unstable version? [y, n]: ")
    hide_stable_version = console.get_response_yes_or_no()
    game_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"] or not hide_stable_version, versions["game"])))

    console.print("\nGame Version (Default: Latest):\n")
    selected_game_version = console.get_response_sequence(game_versions, 1)

    loader_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"], versions["loader"])))
    console.print("\nLoader Version (Default: Latest):\n")
    selected_loader_version = console.get_response_sequence(loader_versions, 1)

    selected_installer_version = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"], versions["installer"])))[0]

    xms, xmx = server.ask_memory()
    server.show_server_info(f"Software: Fabric\nGame Version: {selected_game_version}\nLoader Version: {selected_loader_version}\nInstaller Version: {selected_installer_version}\n", xms, xmx)
    path = server.ask_server_path()

    jar_path = download(connection, selected_game_version, selected_loader_version, selected_installer_version, path)
    connection.close()

    server.write_run_batch(path, xms, xmx, jar_path, True)
    server.launch_server(path)