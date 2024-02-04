from tkinter import Listbox, Tk
from tkinter.ttk import Button

from src.gui.select_software import SelectSoftware
from src.gui.select_version import SelectVersion
from src.gui.util import center_window

root = Tk()
root.title("Minecraft Server Launcher")
root.geometry(center_window(root, 600, 500))
root.resizable(False, False)

server_list = Listbox(root, activestyle="none", height=0, takefocus=False, relief="flat")

def add_server():
    add_server_btn.state(["disabled"])

    select_software_window = SelectSoftware(root)
    software = select_software_window.get_software()

    select_version_window = SelectVersion(root, software)
    version = select_version_window.get_version()

    name = select_software_window.get_server_name()
    server_list.insert(0, name + "-" + software + "-" + version)

    add_server_btn.state(["!disabled"])

add_server_btn = Button(root, text="Add Server", takefocus=False, command=add_server)
add_server_btn.pack()

server_list.pack(fill="x")

root.mainloop()