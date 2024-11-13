# main.py

import tkinter as tk
from ui import ObjectDetectionUI

if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()