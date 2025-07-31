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
        Sidebar(self, self.user_infos)
        #Toolbar(self)
        PlannerBody(self, self.user_infos)
        #FilterBar(self, plannerbody)
        #Settings(self)

class PickingApp(tk.Tk):
    def __init__(self, app_type, user_infos):
        super().__init__()
        self.app_type = app_type
        self.user_infos = user_infos
        self.title("Picking App")
        self.geometry("1920x1080")
        self.configure(bg="white")
        self.create_layout()

    def create_layout(self):
        Header(self, self.app_type, self.user_infos)
        Sidebar(self, self.user_infos)
        #Prodbar(self)
        #Activeref(self)
        PickingBody(self, self.user_infos)

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
        Sidebar(self, self.user_infos)
        #Prodbar(self)
        #Activebox(self)
        PackagingBody(self, self.user_infos)

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
        app = PickingApp(app_type, user_infos)
    elif app_type == "packaging":
        app = PackagingApp(app_type, user_infos)
    
    app.mainloop()

if __name__ == "__main__":
    login_app = LoginApp(launch_main_app)
    login_app.mainloop()