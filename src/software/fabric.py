# https://github.com/FabricMC/fabric-meta#fabric-meta

from argparse import Namespace
from http.client import HTTPSConnection
from os.path import join as path_join
from typing import TypedDict

from src import console, server
from src.util import constants, request, request_download

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
    return request(connection, "/v2/versions")

def get_jar_filename(game_version: str, loader_version: str, installer_version: str):
    return f"fabric-server-mc.{game_version}-loader.{loader_version}-launcher.{installer_version}.jar"

def download(connection: HTTPSConnection, game_version: str, loader_version: str, installer_version: str, path: str):
    jar_filename = get_jar_filename(game_version, loader_version, installer_version)
    request_download(connection, f"/v2/versions/loader/{game_version}/{loader_version}/{installer_version}/server/jar", path_join(path, jar_filename))
    return jar_filename

def cli(args: Namespace, path: str):
    console.print("\rGathering required information...")
    connection = connect()
    versions = get_versions(connection)

    game_versions = tuple(map(lambda x: x["version"], versions["game"]))
    selected_game_version_index = game_versions.index(args.game_version) if args.game_version is not None else 0
    selected_game_version = game_versions[selected_game_version_index]

    loader_versions = tuple(map(lambda x: x["version"], versions["loader"]))
    selected_loader_version_index = loader_versions.index(args.fabric_loader_version) if args.fabric_loader_version is not None else 0
    selected_loader_version = loader_versions[selected_loader_version_index]

    installer_versions = tuple(map(lambda x: x["version"], versions["installer"]))
    selected_installer_version_index = installer_versions.index(args.fabric_installer_version) if args.fabric_installer_version is not None else 0
    selected_installer_version = installer_versions[selected_installer_version_index]

    xmx = args.xmx
    xms = args.xms or xmx
    console.print(" Done\n")
    # server.show_server_info(f"Software: Fabric\nGame Version: {selected_game_version}\nLoader Version: {selected_loader_version}\nInstaller Version: {selected_installer_version}\n", xms, xmx)

    console.print("\rDownloading server jar file...")
    jar_path = download(connection, selected_game_version, selected_loader_version, selected_installer_version, path)
    connection.close()
    console.print(" Done\n")

    console.print("\rWriting batch file...")
    server.write_batch(path, xms, xmx, jar_path, True)
    console.print(" Done\n")

    if args.agree_eula:
        server.write_eula(path)

    if args.launch:
        server.launch(path)