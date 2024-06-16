# https://piston-meta.mojang.com/mc/game/version_manifest.json
# https://files.betacraft.uk/server-archive

# https://minecraft.wiki/w/Version_manifest.json
# https://minecraft.wiki/w/Client.json

from argparse import Namespace
from datetime import datetime
from http.client import HTTPSConnection
from os.path import join as path_join
from typing import Literal, TypedDict

from src import console, server
from src.util import constants, request, request_download, url_path

class ClientJSONDownloadInfo(TypedDict):
    url: str

class ClientJSONDownload(TypedDict):
    client: ClientJSONDownloadInfo
    server: ClientJSONDownloadInfo

class ClientJSONVersion(TypedDict):
    id: str
    url: str

class ClientJSON(TypedDict):
    assetIndex: ClientJSONVersion
    downloads: ClientJSONDownload

class Latest(TypedDict):
    release: str
    snapshot: str

# V1
class ManifestVersionInfo(TypedDict):
    id: str
    type: Literal["release", "snapshot"]
    url: str
    time: str
    releaseTime: str

class VersionManifest(TypedDict):
    latest: Latest
    versions: list[ManifestVersionInfo]

def connect():
    """piston-meta.mojang.com"""
    return HTTPSConnection(constants.VANILLA_META_DOMAIN)

def connect_data():
    """piston-data.mojang.com"""
    return HTTPSConnection(constants.VANILLA_DATA_DOMAIN)

def connect_launchermeta():
    """launchermeta.mojang.com"""
    return HTTPSConnection(constants.VANILLA_LAUNCHER_META_DOMAIN)

def connect_betacraft():
    """files.betacraft.uk"""
    return HTTPSConnection(constants.VANILLA_BETACRAFT_DOMAIN)

def get_version_manifest(connection: HTTPSConnection) -> VersionManifest:
    """piston-meta.mojang.com"""
    return request(connection, "/mc/game/version_manifest.json")

def get_client_json(connection: HTTPSConnection, version: ManifestVersionInfo) -> ClientJSON:
    """piston-meta.mojang.com"""
    return request(connection, url_path(version["url"]))

def is_support_server(version: ManifestVersionInfo):
    return datetime.fromisoformat(version["releaseTime"]) >= constants.FIRST_SERVER_JAR_RELEASED

def download(data_connection: HTTPSConnection, client_json: ClientJSON, filepath: str):
    request_download(data_connection, url_path(client_json["downloads"]["server"]["url"]), filepath)

def download_client(data_connection: HTTPSConnection, client_json: ClientJSON, filepath: str):
    if "client" in (downloads := client_json["downloads"]):
        request_download(data_connection, url_path(downloads["client"]["url"]), filepath)

def download_betacraft(betacraft_connection: HTTPSConnection, version: str, filepath: str):
    request_download(betacraft_connection, f"/server-archive/release/{version}/{"1.0.0" if version == "1.0" else version}.jar", filepath)

def cli(args: Namespace, path: str):
    console.print("\rGathering required information...")
    meta_con = connect()
    version_manifest = get_version_manifest(meta_con)
    supports_server_versions = tuple(filter(is_support_server, version_manifest["versions"]))
    supports_server_versions_id = tuple(map(lambda v: v["id"], supports_server_versions))

    selected_version_index = supports_server_versions_id.index(args.game_version) if args.game_version is not None else 0
    selected_version = supports_server_versions[selected_version_index]

    xmx = args.xmx
    xms = args.xms or xmx

    # system("cls")
    # console.print(f"Software: Vanilla\nGame Version: {selected_version["id"]}\nXms: {xms}G\nXmx: {xmx}G\n\n")
    # system("pause")

    client_json = get_client_json(meta_con, selected_version)
    meta_con.close()
    console.print(" Done\n")

    console.print("\rDownloading server jar file...")
    jar_filepath = path_join(path, "server.jar")

    data_con = connect_data()
    download(data_con, client_json, jar_filepath)
    data_con.close()

    console.print(" Done\n")

    console.print("\rWriting batch file...")
    server.write_batch(path, xms, xmx, jar_filepath, True)
    console.print(" Done\n")

    released_time = datetime.fromisoformat(selected_version["releaseTime"])
    if args.agree_eula and (released_time is None or server.is_need_eula(released_time)):
        server.write_eula(path)

    if args.launch:
        server.launch(path)