import tkinter as tk
from app_UI import MusicAppUI, WelcomeScreen  

def center_window(root, width=1600, height=900):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    center_window(root, 1600, 900)  
    def start_app():
        MusicAppUI(root)
    WelcomeScreen(root, on_enter=start_app)
    root.mainloop()

