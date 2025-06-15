#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#002147", width=120)
        self.pack(side="left", fill="y")
        self.create_widgets()

    def create_widgets(self):
        
        def command():
            print("Home button clicked")
        
        
        
        # MENU Label
        menu_label = tk.Label(self, text="MENU", bg="#002147", fg="white", font=("Arial", 20, "bold"))
        menu_label.pack(pady=(10, 0))

        # Orange Line under MENU (like in the image)
        line = tk.Frame(self, bg="#f57c00", height=4)  # Adjust height as needed
        line.pack(fill="x", padx=10, pady=(5, 20))
                
        # Load icons (resize to fit nicely)
        self.home_icon = ImageTk.PhotoImage(Image.open("../icons/home.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.data_icon = ImageTk.PhotoImage(Image.open("../icons/data.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.edit_icon = ImageTk.PhotoImage(Image.open("../icons/search.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.settings_icon = ImageTk.PhotoImage(Image.open("../icons/settings.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.out_icon = ImageTk.PhotoImage(Image.open("../icons/loginout.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.exit_icon = ImageTk.PhotoImage(Image.open("../icons/exit.png").resize((24, 24), Image.Resampling.LANCZOS))


        # Text button
        home_btn = tk.Button(self, text="  Home", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.home_icon, compound="left", anchor="w")
        home_btn.pack(side="top", fill="x", pady=(10, 0))
        data_btn = tk.Button(self, text="  Data", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.data_icon, compound="left", anchor="w")
        data_btn.pack(side="top", fill="x", pady=(10, 0))
        edit_btn = tk.Button(self, text="  Edit", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.edit_icon, compound="left", anchor="w")
        edit_btn.pack(side="top", fill="x", pady=(10, 0))
        settings_btn = tk.Button(self, text="  Settings", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.settings_icon, compound="left", anchor="w")
        settings_btn.pack(side="top", fill="x", pady=(10, 0))
        
        
        
        

        out_btn = tk.Button(self, text="  Login OUT", bg="#e60000", fg="white",
                        font=("Arial", 10, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.out_icon, compound="left", anchor="w")
        out_btn.pack(side="bottom", fill="x", pady=(10, 0))
        exit_btn = tk.Button(self, text="  Login OUT", bg="white", fg="black",
                        font=("Arial", 10, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.exit_icon, compound="left", anchor="w")
        exit_btn.pack(side="bottom", fill="x", pady=(10, 0))
