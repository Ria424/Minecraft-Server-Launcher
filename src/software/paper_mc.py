# https://api.papermc.io/docs/swagger-ui/index.html?configUrl=/openapi/swagger-config

from http.client import HTTPSConnection
from json import loads as json_loads
from typing import Literal, TypedDict

from src import config, console, server
from src.util import constants

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

def get_projects(connection: HTTPSConnection) -> tuple[str, ...]:
    connection.request("GET", "/v2/projects")
    return json_loads(connection.getresponse().read())["projects"]

# def get_projects():
#     return ("paper", "waterfall", "velocity", "travertine", "folia",)

def get_project(connection: HTTPSConnection, project: str) -> Project:
    connection.request("GET", f"/v2/projects/{project}")
    return json_loads(connection.getresponse().read())

def get_game_versions(connection: HTTPSConnection, project: str, family: str) -> list[str]:
    connection.request("GET", f"/v2/projects/{project}/version_group/{family}")
    return json_loads(connection.getresponse().read())["versions"]

def get_builds(connection: HTTPSConnection, project: str, version: str) -> list[Build]:
    connection.request("GET", f"/v2/projects/{project}/versions/{version}/builds")
    return json_loads(connection.getresponse().read())["builds"]

# def get_build(connection: HTTPSConnection, project: str, version: str, build: int) -> Build:
#     connection.request("GET", f"/v2/projects/{project}/versions/{version}/builds/{build}")
#     return json_loads(connection.getresponse().read())

def download(connection: HTTPSConnection, project_id: str, game_version: str, build: int, path: str):
    jar_file_name = f"{project_id}-{game_version}-{build}.jar"
    connection.request("GET", f"/v2/projects/{project_id}/versions/{game_version}/builds/{build}/downloads/{jar_file_name}")
    with open(path + "/" + jar_file_name, "wb") as jar:
        jar.write(connection.getresponse().read())
    return jar_file_name

def cli():
    connection = connect()

    projects = get_projects(connection)
    console.print("\nProject (Default: paper):\n")
    # selected_project_id = projects[console.get_response_iterable(projects, projects.index(config.default_paper_mc_project) + 1) - 1]
    selected_project_id = console.get_response_sequence(projects, projects.index(config.default_paper_mc_project) + 1)

    project = get_project(connection, selected_project_id)

    console.print("\nVersion Group (Default: Latest):\n")
    selected_version_group = project["version_groups"][console.get_response_iterable(project["version_groups"]) - 1]

    game_versions = get_game_versions(connection, selected_project_id, selected_version_group)
    console.print("\nGame Version (Default: Latest):\n")
    selected_game_version = console.get_response_sequence(game_versions)

    builds = get_builds(connection, selected_project_id, selected_game_version)

    oldest_build = builds[0]["build"]
    latest_build = builds[-1]["build"]
    msg = f"\nBuild [{oldest_build} ~ {latest_build}] (Default: Latest): "

    def get_response_build() -> Build:
        console.print(msg)
        build = builds[min(len(builds) - 1, max(0, console.get_response(latest_build) - oldest_build))]
        if build["channel"] == "experimental":
            console.print("\nThe selected build is experimental. Proceed? [y, n]: ")
            if not console.get_response_yes_or_no():
                build = get_response_build()
        return build
    selected_build = get_response_build()

    xms, xmx = server.ask_memory()
    server.show_server_info(f"Software: {selected_project_id}\nGame Version: {selected_game_version}\nBuild: {selected_build["build"]}\n", xms, xmx)
    path = server.ask_server_path()

    jar_path = download(connection, selected_project_id, selected_game_version, selected_build["build"], path)
    connection.close()

    server.write_run_batch(path, xms, xmx, jar_path, True)
    server.launch_server(path)