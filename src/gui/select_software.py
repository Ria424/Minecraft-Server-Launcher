from tkinter import Label, StringVar
from tkinter.ttk import Button, Combobox, Entry

from src.config import default_software
from src.gui.dialog import Dialog
from src.software import softwares

class SelectSoftware(Dialog):
    def __init__(self, master):
        super().__init__(master, 300, 150, "Minecraft Server Launcher - Select Software")

        Label(self, text="Name:").place(x=50, y=10)

        self.name_var = StringVar(self)
        self.version_var = StringVar(self, default_software)

        Entry(self, textvariable=self.name_var).place(x=100, y=10)

        Label(self, text="Software:").place(x=50, y=50)

        self.software_list = Combobox(self, values=softwares, state="readonly", textvariable=self.version_var)
        self.software_list.set(default_software)
        self.software_list.place(x=110, y=50, width=100)

        Button(self, text="Next", command=self.destroy).place(relx=0.5, y=100, anchor="center")

        self.focus()

    def get_server_name(self):
        return self.name_var.get()

    def get_software(self):
        return self.version_var.get()