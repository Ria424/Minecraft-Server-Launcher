from os import startfile, system
from sys import stdin, stdout
from tkinter.filedialog import askdirectory
from typing import Any

from src import config, console
from src.servers import fabric, paper_mc, server_id

input = stdin.readline
print = stdout.write

paper_mc_projects = paper_mc.get_projects()

servers: list[str] = []
servers.extend(paper_mc_projects)
servers.append("fabric")

print("Server Software (Default: %s):\n" % config.default_software)
selected_server = servers[console.ask_iterable(servers, servers.index(config.default_software) + 1) - 1]

selected_server_id = server_id.VANILLA
if selected_server in paper_mc_projects:
    selected_server_id = server_id.PAPER_MC
elif selected_server == "fabric":
    selected_server_id = server_id.FABRIC

data: Any = None
match selected_server_id:
    case server_id.PAPER_MC:
        data = paper_mc.ask(selected_server)
    case server_id.FABRIC:
        data = fabric.ask()

print("\nXms(G): ")
xms = console.ask(-1)

print("\nXmx(G) (Default: %d): " % config.default_xmx)
xmx = console.ask(config.default_xmx)

system("cls")
match selected_server_id:
    case server_id.PAPER_MC:
        paper_mc.show_server_info(data)
    case server_id.FABRIC:
        fabric.show_server_info(data)
if xms != -1:
    print("Xms: %dG\n" % xms)
print("Xmx: %dG\n\n" % xmx)
system("pause")

path = askdirectory(title="Select Server Directory.")
match selected_server_id:
    case server_id.PAPER_MC:
        paper_mc.create_server(data.project_id, data.game_version, data.build["build"], path, xmx, xms)
    case server_id.FABRIC:
        fabric.create_server(data.game_version, data.loader_version, data.installer_version, path, xmx, xms)

print("\nLaunch server? [y, n]: ")
if console.ask_yes_no():
    print("\nDo you agree with the EULA? [y, n]: ")
    if console.ask_yes_no():
        with open(path + "/eula.txt", "w") as eula_txt:
            eula_txt.write("eula=true")

    startfile(path + "/run.bat", cwd=path)