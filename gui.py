#!/usr/bin/python3


import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from build.header import Header
from build.sidebar import Sidebar        
from build.toolbar import Toolbar
from build.filterbar import FilterBar        
from build.plannerbody import PlannerBody
from build.prodbar import Prodbar
from build.activeref import Activeref
from build.pickingbody import PickingBody
from build.packagingbody import PackagingBody
from build.login import LoginApp
from build.activebox import Activebox
from build.settings import Settings
from models.engine.app_tools import load_settings



class ProductionPlannerApp(tk.Tk):
    def __init__(self, app_type, user_infos):
        super().__init__()
        self.app_type = app_type
        self.user_infos = user_infos
        self.title("Production Planner")
        self.geometry("1100x600")
        self.configure(bg="white")
        self.create_layout()

    def create_layout(self):
        Header(self, self.app_type, self.user_infos)
        Sidebar(self, self.user_infos, self.show_body)
        # body frame
        self.body_frame = tk.Frame(self, bg="white")
        self.body_frame.pack(side="right", fill=tk.BOTH, expand=True)
        
        self.show_body("home")

    def show_body(self, section):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        if section == "home":
            PlannerBody(self.body_frame, self.user_infos)
        elif section == "data":
            tk.Label(self.body_frame, text="DATA FRAME", font=("Arial", 20)).pack(expand=True)
        elif section == "edit":
            tk.Label(self.body_frame, text="EDIT FRAME", font=("Arial", 20)).pack(expand=True)
        elif section == "settings":
            Settings(self.body_frame)

class PickingApp(tk.Tk):
    def __init__(self, app_type, user_infos, picking_type):
        super().__init__()
        self.app_type = app_type
        self.user_infos = user_infos
        self.picking_type = picking_type
        self.title("Picking App")
        self.geometry("1920x1080")
        self.configure(bg="white")
        self.create_layout()

    def create_layout(self):
        Header(self, self.app_type, self.user_infos)
        Sidebar(self, self.user_infos, self.show_body)
        # body frame
        self.body_frame = tk.Frame(self, bg="white")
        self.body_frame.pack(side="right", fill=tk.BOTH, expand=True)
        self.show_body("home")

    def show_body(self, section):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        if section == "home":
            PickingBody(self.body_frame, self.user_infos, self.picking_type)
        elif section == "data":
            tk.Label(self.body_frame, text="DATA FRAME", font=("Arial", 20)).pack(expand=True)
        elif section == "edit":
            tk.Label(self.body_frame, text="EDIT FRAME", font=("Arial", 20)).pack(expand=True)
        elif section == "settings":
            Settings(self.body_frame)

class PackagingApp(tk.Tk):
    def __init__(self, app_type, user_infos):
        super().__init__()
        self.app_type = app_type
        self.user_infos = user_infos
        self.title("Packaging App")
        self.geometry("1920x1080")
        self.configure(bg="white")
        self.create_layout()

    def create_layout(self):
        Header(self, self.app_type, self.user_infos)
        Sidebar(self, self.user_infos, self.show_body)
        # body frame
        self.body_frame = tk.Frame(self, bg="white")
        self.body_frame.pack(side="right", fill=tk.BOTH, expand=True)
        self.show_body("home")

    def show_body(self, section):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        if section == "home":
            PackagingBody(self.body_frame, self.user_infos)
        elif section == "data":
            tk.Label(self.body_frame, text="DATA FRAME", font=("Arial", 20)).pack(expand=True)
        elif section == "edit":
            tk.Label(self.body_frame, text="EDIT FRAME", font=("Arial", 20)).pack(expand=True)
        elif section == "settings":
            Settings(self.body_frame)

def launch_main_app(user_infos):
    print(f"Logged in as: {user_infos}")
    
    app_config = load_settings()
    try:
        app_type = app_config["AppSettings"]["app_type"]
    except:
        app_type = ""

    # Pass the username into your main app if needed
    if app_type == "orders_manager":
        app = ProductionPlannerApp(app_type, user_infos)
    elif app_type == "picking":
        try:
            picking_type = app_config["AppSettings"]["picking_type"]
        except:
            picking_type = "local"
        app = PickingApp(app_type, user_infos, picking_type)
    elif app_type == "packaging":
        app = PackagingApp(app_type, user_infos)
    
    app.mainloop()

if __name__ == "__main__":
    login_app = LoginApp(launch_main_app)
    login_app.mainloop()