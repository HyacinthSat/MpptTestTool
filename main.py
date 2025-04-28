from mppt_gui import MPPT_GUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = MPPT_GUI(root)
    root.mainloop()