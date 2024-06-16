from datetime import datetime
from os import startfile
from os.path import join as path_join

from src.server import jvm_args
from src.util.constants import ADDED_EULA

def is_need_eula(date: datetime):
    return date >= ADDED_EULA

def write_eula(path: str):
    with open(path_join(path, "eula.txt"), "w") as eula_txt:
        eula_txt.write("eula=true")

def launch(path: str):
    startfile(path_join(path, "run.bat"), cwd=path)

def write_batch(path: str, xms: int, xmx: int, jar: str, nogui: bool = False):
    args = []
    if xms > 0:
        args.append(jvm_args.xms(xms))
    if xmx > 0:
        args.append(jvm_args.xmx(xmx))
    args.append(f"-jar {jar}")
    if nogui:
        args.append("nogui")
    with open(path_join(path, "run.bat"), "w") as f:
        f.write(f"@echo off\njava {" ".join(args)}\npause")