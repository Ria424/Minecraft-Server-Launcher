# https://github.com/FabricMC/fabric-meta#fabric-meta

from dataclasses import dataclass
from http.client import HTTPSConnection
from json import loads as json_loads
from typing import TypedDict

from src import console, server

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

@dataclass(repr=False, eq=False, slots=True)
class FabricData:
    versions: Versions
    game_version: str
    loader_version: str
    installer_version: str

    def get_jar_filename(self):
        return f"fabric-server-mc.{self.game_version}-loader.{self.loader_version}-launcher.{self.installer_version}.jar"

    def __repr__(self):
        return f"Software: Fabric\nGame Version: {self.game_version}\nLoader Version: {self.loader_version}\nInstaller Version: {self.installer_version}\n"

def connect():
    return HTTPSConnection("meta.fabricmc.net")

def get_versions(connection: HTTPSConnection) -> Versions:
    connection.request("GET", "/v2/versions")
    return json_loads(connection.getresponse().read())

def download(connection: HTTPSConnection, data: FabricData, path: str):
    jar_filename = data.get_jar_filename()
    connection.request("GET", f"/v2/versions/loader/{data.game_version}/{data.loader_version}/{data.installer_version}/server/jar")
    with open(path + "/" + jar_filename, "wb") as jar:
        jar.write(connection.getresponse().read())
    return jar_filename

def cli():
    connection = connect()
    versions = get_versions(connection)
    connection.close()

    console.print("\nHide unstable version? [y, n]: ")
    hide_stable_version = console.get_response_yes_or_no()
    game_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"] or not hide_stable_version, versions["game"])))

    console.print("\nGame Version (Default: Latest):\n")
    selected_game_version = console.get_response_sequence(game_versions, 1)

    loader_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"], versions["loader"])))
    console.print("\nLoader Version (Default: Latest):\n")
    selected_loader_version = console.get_response_sequence(loader_versions, 1)

    selected_installer_version = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"], versions["installer"])))[0]

    data = FabricData(versions, selected_game_version, selected_loader_version, selected_installer_version,)

    xms, xmx = server.ask_memory()
    server.show_server_info(repr(data), xms, xmx)
    path = server.ask_server_path()
    server.write_run_batch(path, xms, xmx, download(connection, data, path), True)
    server.launch_server(path, data.game_version)