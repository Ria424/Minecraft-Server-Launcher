# https://api.papermc.io/docs/swagger-ui/index.html?configUrl=/openapi/swagger-config

from argparse import Namespace
from http.client import HTTPSConnection
from os.path import join as path_join
from typing import Literal, TypedDict

from src import console, server
from src.util import constants, request, request_download

class Project(TypedDict):
    project_id: str
    project_name: str
    version_groups: list[str]
    versions: list[str]

class BuildChange(TypedDict):
    commit: str
    summary: str
    message: str

class BuildDownload(TypedDict):
    name: str
    sha256: str

class BuildDownloads(TypedDict):
    application: BuildDownload
    # mojang-mappings: BuildDownload

class Build(TypedDict):
    build: int
    time: str
    channel: Literal["default", "experimental"]
    promoted: bool
    changes: list[BuildChange]
    downloads: BuildDownloads

def connect():
    return HTTPSConnection(constants.PAPERMC_API_DOMAIN)

_get_project_cache = None
def get_projects(connection: HTTPSConnection) -> list[str]:
    global _get_project_cache
    if _get_project_cache is None:
        _get_project_cache = request(connection, "/v2/projects")["projects"]
    return _get_project_cache

# def get_projects():
#     return ("paper", "waterfall", "velocity", "travertine", "folia",)

def get_project(connection: HTTPSConnection, project: str) -> Project:
    return request(connection, f"/v2/projects/{project}")

# def get_game_versions_from_family(connection: HTTPSConnection, project: str, family: str) -> list[str]:
#     return request(connection, f"/v2/projects/{project}/version_group/{family}")["versions"]

def get_builds(connection: HTTPSConnection, project: str, version: str) -> list[Build]:
    return request(connection, f"/v2/projects/{project}/versions/{version}/builds")["builds"]

# def get_build(connection: HTTPSConnection, project: str, version: str, build: int) -> Build:
#     return request(connection, f"/v2/projects/{project}/versions/{version}/builds/{build}")

def download(connection: HTTPSConnection, project_id: str, game_version: str, build: int, path: str):
    jar_file_name = f"{project_id}-{game_version}-{build}.jar"
    request_download(connection, f"/v2/projects/{project_id}/versions/{game_version}/builds/{build}/downloads/{jar_file_name}", path_join(path, jar_file_name))
    return jar_file_name

def cli(args: Namespace, path: str):
    console.print("\rGathering required information...")
    connection = connect()

    projects = get_projects(connection)
    # console.print("\nProject (Default: paper):\n")
    # selected_project_id = projects[console.get_response_iterable(projects, projects.index(config.default_paper_mc_project) + 1) - 1]

    assert args.software in projects
    project = get_project(connection, args.software)

    selected_game_version = args.game_version if args.game_version in project["versions"] else project["versions"][-1]

    builds = get_builds(connection, project["project_id"], selected_game_version)
    selected_build = builds[args.papermc_build]

    xmx = args.xmx
    xms = args.xms or xmx
    # server.show_server_info(f"Software: {project["project_id"]}\nGame Version: {selected_game_version}\nBuild: {selected_build["build"]}\n", xms, xmx)
    console.print(" Done\n")

    console.print("\rDownloading server jar file...")
    jar_path = download(connection, project["project_id"], selected_game_version, selected_build["build"], path)
    connection.close()
    console.print(" Done\n")

    console.print("\rWriting batch file...")
    server.write_batch(path, xms, xmx, jar_path, True)
    console.print(" Done\n")

    if args.agree_eula:
        server.write_eula(path)

    if args.launch:
        server.launch(path)