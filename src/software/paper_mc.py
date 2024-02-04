# https://api.papermc.io/docs/swagger-ui/index.html?configUrl=/openapi/swagger-config

from json import loads as json_loads
from typing import Literal, TypedDict
from urllib.request import urlopen

from src import console

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

class PaperMCData:
    __slots__ = ("project_id", "game_version", "build",)

    def __init__(self, project_id: str, game_version: str, build: Build):
        self.project_id = project_id
        self.game_version = game_version
        self.build = build

PROJECTS_URL = "https://api.papermc.io/v2/projects"
PROJECT_URL = PROJECTS_URL + "/%s"
VERSION_GROUP_URL = PROJECT_URL + "/version_group/%s"
BUILD_VERSIONS_URL = PROJECT_URL + "/versions/%s"
BUILDS_URL = BUILD_VERSIONS_URL + "/builds"
BUILD_URL = BUILDS_URL + "/%d"
DOWNLOAD_URL = BUILD_URL + "/downloads/%s"
JAR_FILENAME = "%s-%s-%d.jar"

def get_projects() -> list[str]:
    return json_loads(urlopen(PROJECTS_URL).read())["projects"]

def get_project(project: str) -> Project:
    return json_loads(urlopen(PROJECT_URL % project).read())

def get_versions(project: str, family: str) -> list[str]:
    return json_loads(urlopen(VERSION_GROUP_URL % (project, family,)).read())["versions"]

def get_builds(project: str, version: str) -> list[Build]:
    return json_loads(urlopen(BUILDS_URL % (project, version,)).read())["builds"]

def get_build(project: str, version: str, build: int) -> Build:
    return json_loads(urlopen(BUILD_URL % (project, version, build,)).read())

def get_jar_name(project: str, version: str, build: int) -> str:
    return JAR_FILENAME % (project, version, build,)

def download(project: str, version: str, build: int, path: str):
    jar_filename = get_jar_name(project, version, build)
    with open(path + "/" + jar_filename, "wb") as jar:
        jar.write(urlopen(DOWNLOAD_URL % (project, version, build, jar_filename)).read())
    return jar_filename

def create_server(project: str, version: str, build: int, path: str, xmx: int, xms: int = -1):
    jar_filename = download(project, version, build, path)
    with open(path + "/run.bat", "w") as bat:
        content = "@echo off\njava"
        if xms != -1:
            content += " -Xms%dG" % xms
        content += " -Xmx%dG -jar %s --nogui\npause" % (xmx, jar_filename,)
        bat.write(content)

def ask(project_id: str):
    project = get_project(project_id)

    console.print("\nVersion Group (Default: Latest):\n")
    selected_version_group = project["version_groups"][console.ask_iterable(project["version_groups"]) - 1]

    versions = get_versions(project_id, selected_version_group)

    console.print("\nVersion (Default: Latest):\n")
    selected_version = versions[console.ask_iterable(versions) - 1]

    builds = get_builds(project_id, selected_version)
    oldest_build = builds[0]["build"]
    latest_build = builds[-1]["build"]
    msg = "\nBuild [%d ~ %d] (Default: Latest): " % (oldest_build, latest_build,)

    def ask_build():
        console.print(msg)
        build = builds[min(len(builds) - 1, max(0, console.ask(latest_build) - oldest_build))]
        if build["channel"] == "experimental":
            console.print("\nThe selected build is experimental. Proceed? [y, n]: ")
            if not console.ask_yes_no():
                build = ask_build()
        return build
    selected_build = ask_build()

    return PaperMCData(project_id, selected_version, selected_build)

def show_server_info(data: PaperMCData):
    console.print("Software: %s\nGame Version: %s\nBuild: %d\n" % (data.project_id, data.game_version, data.build["build"],))