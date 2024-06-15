# https://piston-meta.mojang.com/mc/game/version_manifest.json
# https://files.betacraft.uk/server-archive

# https://minecraft.wiki/w/Version_manifest.json
# https://minecraft.wiki/w/Client.json

from datetime import datetime
from http.client import HTTPSConnection
from os import makedirs
from typing import Literal, TypedDict

from src import console, server
from src.util import (connect_with, constants, request, request_download,
                      url_domain, url_path)

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

class ResourceDownloadInfo(TypedDict):
    hash: str
    size: int

class Resources(TypedDict):
    objects: dict[str, ResourceDownloadInfo]

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
    return HTTPSConnection(constants.VANILLA_META_DOMAIN)

def connect_data():
    return HTTPSConnection(constants.VANILLA_DATA_DOMAIN)

def connect_launchermeta():
    return HTTPSConnection(constants.VANILLA_LAUNCHER_META_DOMAIN)

def connect_resource():
    return HTTPSConnection(constants.VANILLA_RESOURCES_DOMAIN)

def connect_betacraft():
    return HTTPSConnection(constants.VANILLA_BETACRAFT_DOMAIN)

def get_version_manifest(connection: HTTPSConnection) -> VersionManifest:
    """piston-meta.mojang.com"""
    return request(connection, "/mc/game/version_manifest.json")

def get_client_json(connection: HTTPSConnection, version: ManifestVersionInfo) -> ClientJSON:
    """piston-meta.mojang.com"""
    return request(connection, url_path(version["url"]))

def find_version(versions: list[ManifestVersionInfo], needle: str):
    for version in versions:
        if version["id"] == needle:
            return version
    return None

def is_support_server(version: ManifestVersionInfo):
    return datetime.fromisoformat(version["releaseTime"]) >= constants.FIRST_SERVER_JAR_RELEASED

def download(data_connection: HTTPSConnection, client_json: ClientJSON, filepath: str):
    request_download(data_connection, url_path(client_json["downloads"]["server"]["url"]), filepath)

def download_client(data_connection: HTTPSConnection, client_json: ClientJSON, filepath: str):
    if "client" in (downloads := client_json["downloads"]):
        request_download(data_connection, url_path(downloads["client"]["url"]), filepath)

def download_betacraft(betacraft_connection: HTTPSConnection, version: str, filepath: str):
    request_download(betacraft_connection, f"/server-archive/release/{version}/{"1.0.0" if version == "1.0" else version}.jar", filepath)

def download_resources(asset_index_url: str, path: str):
    """`asset_index_url` must be a full URL."""
    with connect_with(url_domain(asset_index_url)) as ast_con:
        resources: Resources = request(ast_con, url_path(asset_index_url))

    with connect_with(constants.VANILLA_RESOURCES_DOMAIN) as res_con:
        for filename, info in resources["objects"].items():
            if '/' in filename:
                makedirs(f"{path}/{filename[:filename.rindex('/')]}", exist_ok=True)
            request_download(res_con, f"{info["hash"][:1]}{info["hash"]}", f"{path}/{filename}")

def cli():
    meta_con = HTTPSConnection(constants.VANILLA_META_DOMAIN)
    version_manifest = get_version_manifest(meta_con)
    supports_server_versions = tuple(filter(is_support_server, version_manifest["versions"]))

    console.print("\nGame Version (Default: Latest):\n")
    selected_version_index = console.get_response_iterable(map(lambda x: x["id"], supports_server_versions), 1) - 1
    selected_version = tuple(supports_server_versions)[selected_version_index]

    xms, xmx = server.ask_memory()
    server.show_server_info(f"Software: Vanilla\nGame Version: {selected_version["id"]}\n", xms, xmx)
    path = server.ask_server_path()

    client_json = get_client_json(meta_con, selected_version)
    jar_filepath = f"{path}/server.jar"
    with connect_with(constants.VANILLA_DATA_DOMAIN) as data_con:
        download(data_con, client_json, jar_filepath)

    meta_con.close()

    server.write_run_batch(path, xms, xmx, jar_filepath, True)
    server.launch_server(path, datetime.fromisoformat(selected_version["releaseTime"]))