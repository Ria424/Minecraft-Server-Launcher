from tkinter import Misc

def center_window(master: Misc, width: int, height: int):
    return "%dx%d+%d+%d" % (width, height, (master.winfo_screenwidth() - width) // 2, (master.winfo_screenheight() - height) // 2,)