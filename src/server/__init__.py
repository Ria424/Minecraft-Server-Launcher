from datetime import datetime
from os import startfile, system
from tkinter.filedialog import askdirectory

from src import config, console
from src.minecraft_version import ADDED_EULA
from src.server import jvm_args

def ask_memory():
    console.print("\nXms(G): ")
    xms = console.get_response(0)

    console.print(f"\nXmx(G) (Default: {config.default_xmx}): ")
    xmx = console.get_response(config.default_xmx)

    return (xms, xmx,)

def show_server_info(info: str, xms: int, xmx: int):
    system("cls")
    console.print(info)

    if xms > 0:
        console.print(f"Xms: {xms}G\n")
    console.print(f"Xmx: {xmx}G\n\n")
    system("pause")

def ask_server_path():
    return askdirectory(mustexist=True, title="Select Server Directory.")

def launch_server(path: str, released_time: datetime | None = None):
    console.print("\nLaunch server? [y, n]: ")
    if console.get_response_yes_or_no():
        if released_time is not None and released_time >= ADDED_EULA:
            console.print("\nDo you agree with the EULA(https://www.minecraft.net/eula)? [y, n]: ")
            if console.get_response_yes_or_no():
                with open(f"{path}/eula.txt", "w") as eula_txt:
                    eula_txt.write("eula=true")

        startfile(f"{path}/run.bat", cwd=path)

def write_run_batch(path: str, xms: int, xmx: int, jar: str, nogui: bool = False):
    args = []
    if xms > 0:
        args.append(jvm_args.xms(xms))
    if xmx > 0:
        args.append(jvm_args.xmx(xmx))
    args.append(f"-jar {jar}")
    if nogui:
        args.append("nogui")
    with open(f"{path}/run.bat", "w") as f:
        f.write(f"java {" ".join(args)}\npause")