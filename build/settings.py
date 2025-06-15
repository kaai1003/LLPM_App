#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class Settings(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.settings_tabs = ttk.Notebook(self)
        self.settings_tabs.pack(fill="both", expand=True)
        
        self.app_tab = ttk.Frame(self.settings_tabs, style="TNotebook.Tab")
        self.prod_tab = ttk.Frame(self.settings_tabs, style="TNotebook.Tab")
        self.packaging_tab = ttk.Frame(self.settings_tabs, style="TNotebook.Tab")
        self.users_tab = ttk.Frame(self.settings_tabs, style="TNotebook.Tab")
        
        def update():
            pass
        
        self.settings_tabs.add(self.app_tab, text="App Config")
        self.settings_tabs.add(self.prod_tab, text="Production Config")
        self.settings_tabs.add(self.packaging_tab, text="Packaging Config")
        self.settings_tabs.add(self.users_tab, text="Users Config")
        
        self.app_label = tk.Label(self.app_tab, text="General App Setup", bg="#F0F0F0", fg="navy", font=("Helvetica", 20, "bold"))
        self.app_label.pack(pady=10)
        self.prod_label = tk.Label(self.prod_tab, text="Production Configurations", bg="#818181", fg="navy", font=("Helvetica", 20, "bold"))
        self.prod_label.pack(pady=10)
        self.packaging_label = tk.Label(self.packaging_tab, text="Packaging Configurations", bg="#818181", fg="navy", font=("Helvetica", 20, "bold"))
        self.packaging_label.pack(pady=10)
        self.users_label = tk.Label(self.users_tab, text="Users Configurations", bg="#818181", fg="navy", font=("Helvetica", 20, "bold"))
        self.users_label.pack(pady=10)
        # app type and line id 
        self.appconfig_frame = tk.Frame(self.app_tab, bg="#F0F0F0", bd=2, relief="groove")
        self.appconfig_frame.pack(pady=20)
        
        self.apptype_label = tk.Label(self.appconfig_frame, text="App Type:", bg="#F0F0F0", font=("Arial", 12))
        self.apptype_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.apptype_entry = ttk.Combobox(self.appconfig_frame, values=["orders_manager", "picking", "packaging"], state="readonly")
        self.apptype_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.line_label = tk.Label(self.appconfig_frame, text="Line ID:", bg="#F0F0F0", font=("Arial", 12))
        self.line_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.line_entry = ttk.Entry(self.appconfig_frame, font=("Arial", 12))
        self.line_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.line_entry.insert(0, "Enter Line ID")
        self.update_button = tk.Button(self.appconfig_frame, text="Update", command=self.update, bg="blue", fg="white", font=("Arial", 12, "bold"))
        self.update_button.grid(row=2, column=0, columnspan=2, pady=10)
        # database configuration
        self.appdb_label = tk.Label(self.app_tab, text="App Database Setup", bg="#F0F0F0", fg="blue", font=("Helvetica", 20, "bold"))
        self.appdb_label.pack(pady=10)
        
        self.dbconfig_frame = tk.Frame(self.app_tab, bg="#F0F0F0", bd=2, relief="groove")
        self.dbconfig_frame.pack(pady=20)
        
        self.dbname_label = tk.Label(self.dbconfig_frame, text="Database Name:", bg="#F0F0F0", font=("Arial", 12))
        self.dbname_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.dbname_entry = ttk.Entry(self.dbconfig_frame, font=("Arial", 12))
        self.dbname_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.dbuser_label = tk.Label(self.dbconfig_frame, text="User Name:", bg="#F0F0F0", font=("Arial", 12))
        self.dbuser_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.dbuser_entry = ttk.Entry(self.dbconfig_frame, font=("Arial", 12))
        self.dbuser_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.dbpw_label = tk.Label(self.dbconfig_frame, text="User Password:", bg="#F0F0F0", font=("Arial", 12))
        self.dbpw_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.dbpw_entry = ttk.Entry(self.dbconfig_frame, font=("Arial", 12))
        self.dbpw_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.dbhost_label = tk.Label(self.dbconfig_frame, text="Host/IP Adress:", bg="#F0F0F0", font=("Arial", 12))
        self.dbhost_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.dbhost_entry = ttk.Entry(self.dbconfig_frame, font=("Arial", 12))
        self.dbhost_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.dbport_label = tk.Label(self.dbconfig_frame, text="Port:", bg="#F0F0F0", font=("Arial", 12))
        self.dbport_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.dbport_entry = ttk.Entry(self.dbconfig_frame, font=("Arial", 12))
        self.dbport_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        
        self.savedb_button = tk.Button(self.dbconfig_frame, text="Save Database", command=self.update, bg="blue", fg="white", font=("Arial", 12, "bold"))
        self.savedb_button.grid(row=5, column=0, columnspan=1, padx=10, pady=10)
        self.checkdb_button = tk.Button(self.dbconfig_frame, text="Check Connexion", command=self.update, bg="blue", fg="white", font=("Arial", 12, "bold"))
        self.checkdb_button.grid(row=5, column=1, columnspan=1, padx=10, pady=10)