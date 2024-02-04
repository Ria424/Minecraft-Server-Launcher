from os import startfile, system
from tkinter.filedialog import askdirectory
from typing import Any

from src import config, console
from src.software import fabric, paper_mc, paper_mc_projects, software_id, softwares

console.print("Server Software (Default: %s):\n" % config.default_software)
selected_software = softwares[console.ask_iterable(softwares, softwares.index(config.default_software) + 1) - 1]

selected_software_id = software_id.VANILLA
if selected_software in paper_mc_projects:
    selected_software_id = software_id.PAPER_MC
elif selected_software == "fabric":
    selected_software_id = software_id.FABRIC

data: Any = None
match selected_software_id:
    case software_id.PAPER_MC:
        data = paper_mc.ask(selected_software)
    case software_id.FABRIC:
        data = fabric.ask()

console.print("\nXms(G): ")
xms = console.ask(-1)

console.print("\nXmx(G) (Default: %d): " % config.default_xmx)
xmx = console.ask(config.default_xmx)

system("cls")
match selected_software_id:
    case software_id.PAPER_MC:
        paper_mc.show_server_info(data)
    case software_id.FABRIC:
        fabric.show_server_info(data)
if xms != -1:
    console.print("Xms: %dG\n" % xms)
console.print("Xmx: %dG\n\n" % xmx)
system("pause")

path = askdirectory(title="Select Server Directory.")
match selected_software_id:
    case software_id.PAPER_MC:
        paper_mc.create_server(data.project_id, data.game_version, data.build["build"], path, xmx, xms)
    case software_id.FABRIC:
        fabric.create_server(data.game_version, data.loader_version, data.installer_version, path, xmx, xms)

console.print("\nLaunch server? [y, n]: ")
if console.ask_yes_no():
    console.print("\nDo you agree with the EULA? [y, n]: ")
    if console.ask_yes_no():
        with open(path + "/eula.txt", "w") as eula_txt:
            eula_txt.write("eula=true")

    startfile(path + "/run.bat", cwd=path)