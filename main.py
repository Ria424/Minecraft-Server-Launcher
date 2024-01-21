from os import startfile, system
from sys import stdin, stdout
from tkinter.filedialog import askdirectory
from typing import Iterable

from src import config, paper_mc

input = stdin.readline
print = stdout.write
paper_projects = paper_mc.get_projects()

def ask(default: int):
    response = input().rstrip()
    if not response:
        return default
    return int(response)

def ask_iterable(iterable: Iterable[str], default: int = 0):
    for i, text in enumerate(iterable, 1):
        print("[%d] %s\n" % (i, text,))
    response = input(3).rstrip()
    if not response:
        return default
    return int(response)

def ask_yes_no():
    return input(2).rstrip().lower() == "y"

print("Server Software (Default: %s):\n" % config.default_software)
selected_project = paper_projects[ask_iterable(paper_projects, paper_projects.index(config.default_software) + 1) - 1]

project = paper_mc.get_project(selected_project)

print("\nVersion Group (Default: Latest):\n")
selected_version_group = project["version_groups"][ask_iterable(project["version_groups"]) - 1]

versions = paper_mc.get_versions(selected_project, selected_version_group)

print("\nVersion (Default: Latest):\n")
selected_version = versions[ask_iterable(versions) - 1]

builds = paper_mc.get_builds(selected_project, selected_version)
oldest_build = builds[0]["build"]
latest_build = builds[-1]["build"]
msg = "\nBuild [%d ~ %d] (Default: Latest): " % (oldest_build, latest_build,)

def ask_build():
    print(msg)
    build = builds[min(len(builds) - 1, max(0, ask(latest_build) - oldest_build))]
    if build["channel"] == "experimental":
        print("\nThe selected build is experimental. Proceed? [y, n]: ")
        if not ask_yes_no():
            build = ask_build()
    return build
selected_build = ask_build()

print("\nXms(G): ")
xms = ask(-1)

print("\nXmx(G) (Default: 4): ")
xmx = ask(3)

system("cls")

if xms != -1:
    print("Software: %s / Version: %s / Build: %d / Xms: %dG / Xmx: %dG\n\n" % (project["project_name"], selected_version, selected_build["build"], xms, xmx,))
else:
    print("Software: %s / Version: %s / Build: %d / Xmx: %dG\n\n" % (project["project_name"], selected_version, selected_build["build"], xmx,))
system("pause")

dir = askdirectory(title="Select Server Directory.")
paper_mc.download(selected_project, selected_version, selected_build["build"], dir)
jar_name = paper_mc.get_jar_name(selected_project, selected_version, selected_build["build"])

with open(dir + "/run.bat", "w") as bat:
    content = "@echo off\njava"
    if xms != -1:
        content += " -Xms%dG" % xms
    content += " -Xmx%dG -jar %s --nogui\npause" % (xmx, jar_name,)
    bat.write(content)

print("\nLaunch server? [y, n]: ")
if ask_yes_no():
    print("\nDo you agree with the EULA? [y, n]: ")
    if ask_yes_no():
        with open(dir + "/eula.txt", "w") as eula_txt:
            eula_txt.write("eula=true")

    startfile(dir + "/run.bat", cwd=dir)