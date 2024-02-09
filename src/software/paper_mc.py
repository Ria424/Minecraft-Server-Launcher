# https://api.papermc.io/docs/swagger-ui/index.html?configUrl=/openapi/swagger-config

from dataclasses import dataclass
from http.client import HTTPSConnection
from json import loads as json_loads
from typing import Literal, TypedDict

from src import config, console, server

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

@dataclass(repr=False, eq=False, slots=True)
class PaperMCData:
    project_id: str
    game_version: str
    build: Build

    def get_jar_filename(self):
        return f"{self.project_id}-{self.game_version}-{self.build["build"]}.jar"

    def __repr__(self):
        return f"Software: {self.project_id}\nGame Version: {self.game_version}\nBuild: {self.build["build"]}\n"

# PROJECTS_URL = "https://api.papermc.io/v2/projects"
# PROJECT_URL = PROJECTS_URL + "/%s"
# VERSION_GROUP_URL = PROJECT_URL + "/version_group/%s"
# BUILD_VERSIONS_URL = PROJECT_URL + "/versions/%s"
# BUILDS_URL = BUILD_VERSIONS_URL + "/builds"
# BUILD_URL = BUILDS_URL + "/%d"
# DOWNLOAD_URL = BUILD_URL + "/downloads/%s"
# JAR_FILENAME = "%s-%s-%d.jar"
# JVM_ARGS = "java {xms} {xmx} -jar {jar} {nogui}"
# JVM_ARG_PATTERN = {
#     "xmx": "-Xmx%d{unit}",
#     "xms": "-Xms%d{unit}",
#     "nogui": "--nogui"
# }

def connect():
    return HTTPSConnection("api.papermc.io")

def get_projects(connection: HTTPSConnection) -> tuple[str, ...]:
    connection.request("GET", "/v2/projects")
    return json_loads(connection.getresponse().read())["projects"]

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

def download(connection: HTTPSConnection, data: PaperMCData, path: str):
    jar_file_name = data.get_jar_filename()
    connection.request("GET", f"/v2/projects/{data.project_id}/versions/{data.game_version}/builds/{data.build["build"]}/downloads/{jar_file_name}")
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
    selected_game_version = console.get_response_sequence(game_versions, 1)

    builds = get_builds(connection, selected_project_id, selected_game_version)
    connection.close()

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

    data = PaperMCData(selected_project_id, selected_game_version, selected_build)

    xms, xmx = server.ask_memory()
    server.show_server_info(repr(data), xms, xmx)
    path = server.ask_server_path()
    server.write_run_batch(path, xms, xmx, download(connection, data, path), True)
    server.launch_server(path, data.game_version)