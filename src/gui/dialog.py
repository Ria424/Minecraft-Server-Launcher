from tkinter import Tk, Toplevel

from src.gui.util import center_window

class Dialog(Toplevel):
    def __init__(self, master: Tk, width: int, height: int, title: str):
        super().__init__(master)

        self.master = master

        self.geometry(center_window(self, width, height))
        self.title(title)
        self.resizable(False, False)

    def focus(self):
        super().focus()
        self.grab_set()
        self.wait_window()