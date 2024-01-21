from json import loads as json_loads
from typing import Literal, TypedDict
from urllib.request import urlopen

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

PROJECTS_URL = "https://api.papermc.io/v2/projects"
PROJECT_URL = PROJECTS_URL + "/%s"
VERSION_GROUP_URL = PROJECT_URL + "/version_group/%s"
BUILD_VERSIONS_URL = PROJECT_URL + "/versions/%s"
BUILDS_URL = BUILD_VERSIONS_URL + "/builds"
BUILD_URL = BUILDS_URL + "/%d"
DOWNLOAD_URL = BUILD_URL + "/downloads/%s"
JAR_FILENAME = "%s-%s-%d.jar"

@staticmethod
def get_projects() -> list[str]:
    return json_loads(urlopen(PROJECTS_URL).read())["projects"]

@staticmethod
def get_project(project: str) -> Project:
    return json_loads(urlopen(PROJECT_URL % project).read())

@staticmethod
def get_versions(project: str, family: str) -> list[str]:
    return json_loads(urlopen(VERSION_GROUP_URL % (project, family,)).read())["versions"]

@staticmethod
def get_builds(project: str, version: str) -> list[Build]:
    return json_loads(urlopen(BUILDS_URL % (project, version,)).read())["builds"]

@staticmethod
def get_build(project: str, version: str, build: int) -> Build:
    return json_loads(urlopen(BUILD_URL % (project, version, build,)).read())

@staticmethod
def get_jar_name(project: str, version: str, build: int) -> str:
    return JAR_FILENAME % (project, version, build,)

@staticmethod
def download(project: str, version: str, build: int, path: str):
    jar_filename = get_jar_name(project, version, build)
    with open(path + "/" + jar_filename, "wb") as jar:
        jar.write(urlopen(DOWNLOAD_URL % (project, version, build, jar_filename)).read())