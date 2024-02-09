from tkinter import Misc

def center_window(master: Misc, width: int, height: int):
    return f"{width}x{height}+{(master.winfo_screenwidth() - width) // 2}+{(master.winfo_screenheight() - height) // 2}"