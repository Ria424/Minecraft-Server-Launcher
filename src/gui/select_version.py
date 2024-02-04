from tkinter import BooleanVar, StringVar, Tk
from tkinter.ttk import Checkbutton, Combobox, Label

from src.gui.dialog import Dialog
from src.software import fabric, paper_mc, paper_mc_projects

class SelectVersion(Dialog):
    def __init__(self, master: Tk, software: str):
        super().__init__(master, 400, 300, "Minecraft Server Launcher - Select Version")

        self.game_version_var = StringVar(self)

        Label(self, text="Game Version:").place(x=10, y=10)

        self.game_version = Combobox(self, state="readonly", textvariable=self.game_version_var)
        self.game_version.place(x=100, y=10, width=150)

        if software in paper_mc_projects:
            project = paper_mc.get_project(software)
            game_versions = project["versions"]
            game_versions.reverse()

            self.game_version.config(values=game_versions)
            self.game_version.set(game_versions[0])
        elif software == "fabric":
            versions = fabric.get_versions()

            self.snapshot_var = BooleanVar(self, False)

            def load_game_version():
                snapshot_enabled = self.snapshot_var.get()
                game_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"] or snapshot_enabled, versions["game"])))
                self.game_version.config(values=game_versions)

                if not snapshot_enabled:
                    self.game_version.set(game_versions[0])

            Checkbutton(self, text="Snapshot", variable=self.snapshot_var, command=load_game_version).place(x=300, y=10)

            load_game_version()

        self.focus()

    def get_version(self):
        return self.game_version_var.get()