from tkinter import BooleanVar, StringVar, Tk
from tkinter.ttk import Checkbutton, Combobox, Label

from src.gui.dialog import Dialog
from src.software import fabric, forge, paper_mc

class SelectVersion(Dialog):
    def __init__(self, master: Tk, software: str):
        super().__init__(master, 400, 300, "Minecraft Server Launcher - Select Version")

        self.game_version_var = StringVar(self)

        Label(self, text="Game Version:").place(x=10, y=10)

        self.game_version = Combobox(self, state="readonly", textvariable=self.game_version_var)
        self.game_version.place(x=100, y=10, width=150)

        if software in paper_mc.get_projects():
            connection = paper_mc.get_connection()
            project = paper_mc.get_project(connection, software)
            game_versions = project["versions"]
            game_versions.reverse()

            self.game_version.config(values=game_versions)
            self.game_version.set(game_versions[0])
        else:
            match software:
                case "fabric":
                    connection = fabric.get_connection()
                    versions = fabric.get_versions(connection)

                    self.snapshot_var = BooleanVar(self, False)

                    def load_game_version():
                        snapshot_enabled = self.snapshot_var.get()
                        game_versions = tuple(map(lambda x: x["version"], filter(lambda x: x["stable"] or snapshot_enabled, versions["game"])))
                        self.game_version.config(values=game_versions)

                        if not snapshot_enabled:
                            self.game_version.set(game_versions[0])

                    Checkbutton(self, text="Snapshot", variable=self.snapshot_var, command=load_game_version).place(x=300, y=10)

                    load_game_version()
                case "forge":
                    connection = forge.get_connection()
                    game_versions = forge.get_game_versions(connection)
                    self.game_version.config(values=game_versions)

        self.focus()

    def get_version(self):
        return self.game_version_var.get()