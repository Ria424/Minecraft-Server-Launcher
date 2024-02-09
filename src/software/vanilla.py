# https://piston-meta.mojang.com/mc/game/version_manifest.json
# https://minecraft.wiki/w/Version_manifest.json
# https://minecraft.wiki/w/Client.json

from datetime import datetime
from http.client import HTTPSConnection
from json import loads as json_loads
from typing import Literal, TypedDict

from src import console, server
from src.util import url_path

FIRST_SERVER_JAR_RELEASED = datetime.fromisoformat("2012-03-29T22:00:00+00:00")

class Latest(TypedDict):
    release: str
    snapshot: str

# V1
class Version(TypedDict):
    id: str
    type: Literal["release", "snapshot"]
    url: str
    time: str
    releaseTime: str

class VersionManifest(TypedDict):
    latest: Latest
    versions: list[Version]

def connect():
    return HTTPSConnection("piston-meta.mojang.com")

def connect_data():
    return HTTPSConnection("piston-data.mojang.com")

def get_version_manifest(connection: HTTPSConnection) -> VersionManifest:
    connection.request("GET", "/mc/game/version_manifest.json")
    return json_loads(connection.getresponse().read())

def download(connection: HTTPSConnection, data_connection: HTTPSConnection, url: str, path: str):
    connection.request("GET", url)
    data_connection.request("GET", url_path(json_loads(connection.getresponse().read())["downloads"]["server"]["url"]))
    jar_filename = "server.jar"
    with open(f"{path}/{jar_filename}", "wb") as jar:
        jar.write(data_connection.getresponse().read())
    return jar_filename

def cli():
    connection = connect()

    version_manifest = get_version_manifest(connection)
    supports_server_versions = tuple(filter(lambda x: datetime.fromisoformat(x["releaseTime"]) >= FIRST_SERVER_JAR_RELEASED, version_manifest["versions"]))

    console.print("\nGame Version (Default: Latest):\n")
    selected_version_index = console.get_response_iterable(map(lambda x: x["id"], supports_server_versions), 1) - 1
    selected_version = tuple(supports_server_versions)[selected_version_index]

    xms, xmx = server.ask_memory()
    server.show_server_info(f"Software: Vanilla\nGame Version: {selected_version["id"]}\n", xms, xmx)
    path = server.ask_server_path()

    data_connection = connect_data()
    jar_filename = download(connection, data_connection, url_path(selected_version["url"]), path)
    connection.close()
    data_connection.close()

    server.write_run_batch(path, xms, xmx, jar_filename, True)
    server.launch_server(path, datetime.fromisoformat(selected_version["releaseTime"]))