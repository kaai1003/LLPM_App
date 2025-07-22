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
from build.activebox import Activebox
from build.settings import Settings
from models.engine.app_tools import load_settings



class ProductionPlannerApp(tk.Tk):
    def __init__(self, app_type):
        super().__init__()
        self.app_type = app_type
        self.title("Production Planner")
        self.geometry("1100x600")
        self.configure(bg="white")
        self.create_layout()

    def create_layout(self):
        Header(self, self.app_type)
        Sidebar(self)
        #Toolbar(self)
        PlannerBody(self)
        #FilterBar(self, plannerbody)
        #Settings(self)

class PickingApp(tk.Tk):
    def __init__(self, app_type):
        super().__init__()
        self.app_type = app_type
        self.title("Picking App")
        self.geometry("1920x1080")
        self.configure(bg="white")
        self.create_layout()

    def create_layout(self):
        Header(self, self.app_type)
        Sidebar(self)
        #Prodbar(self)
        #Activeref(self)
        PickingBody(self)

class PackagingApp(tk.Tk):
    def __init__(self, app_type):
        super().__init__()
        self.app_type = app_type
        self.title("Packaging App")
        self.geometry("1920x1080")
        self.configure(bg="white")
        self.create_layout()

    def create_layout(self):
        Header(self, self.app_type)
        Sidebar(self)
        #Prodbar(self)
        #Activebox(self)
        PackagingBody(self)

if __name__ == "__main__":
    app_config = load_settings()
    try:
        app_type = app_config["AppSettings"]["app_type"]
    except:
        app_type = ""
    print(f"App type: {app_type}")
    if app_type == "orders_manager":
        app = ProductionPlannerApp(app_type)
    elif app_type == "picking":
        app = PickingApp(app_type)
    elif app_type == "packaging":
        app = PackagingApp(app_type)
    app.mainloop()