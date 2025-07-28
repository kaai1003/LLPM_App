#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from functools import partial
from models.engine.app_tools import set_dashboard_config

class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#002147", width=120)
        self.pack(side="left", fill="y")
        self.create_widgets()

    def create_widgets(self):
        
        def command(btn):
            if btn == "dashboard":
                print("dashboard button clicked")
                create_dashboard_popup()
        
        def set_config(ts, ops, pops, st, ht, eff):
            dashboard_settings = {}
            if ts == "":
                tk.Label(self.popup, text="Error: Team Speaker is required.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Team Speaker is required")
                return
            dashboard_settings["team_speaker"] = ts
            if ops == "":
                tk.Label(self.popup, text="Error: Line Operators is required.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Line Operators is required")
                return
            try:
                ops = int(ops)
            except ValueError:
                tk.Label(self.popup, text="Error: Line Operators must be a number.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Line Operators must be a number")
                return
            dashboard_settings["line_operators"] = ops
            if pops == "":
                tk.Label(self.popup, text="Error: Present Operators is required.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Present Operators is required")
                return
            try:
                pops = int(pops)
            except ValueError:
                tk.Label(self.popup, text="Error: Present Operators must be a number.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Present Operators must be a number")
                return
            if ops < pops:
                tk.Label(self.popup, text="Error: Present Operators must be <= Line Operators.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Present Operators must be <= Line Operators")
                return
            dashboard_settings["present_operators"] = pops
            if st == "":
                tk.Label(self.popup, text="Error: Shift Target is required.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Shift Target is required")
                return
            try:
                st = int(st)
            except ValueError:
                tk.Label(self.popup, text="Error: Shift Target must be a number.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Shift Target must be a number")
                return
            dashboard_settings["shift_target"] = st
            if ht == "":
                tk.Label(self.popup, text="Error: Target/Hour is required.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Target/Hour is required")
                return
            try:
                ht = int(ht)
            except ValueError:
                tk.Label(self.popup, text="Error: Target/Hour must be a number.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Target/Hour must be a number")
                return
            dashboard_settings["target_per_hour"] = ht
            if eff == "":
                tk.Label(self.popup, text="Error: Effecience is required.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Effecience is required")
                return
            try:
                eff = int(eff)
            except ValueError:
                tk.Label(self.popup, text="Error: Effecience must be a number.", fg="red").grid(row=7, columnspan=2, pady=10)
                print("Effecience must be a number")
                return
            dashboard_settings["effecience"] = eff
            set_dashboard_config(dashboard_settings)
            print("Dashboard Settings Updated:", dashboard_settings)
            self.popup.destroy()
            
        def cancel():
            print("cancel Dashboard Settings")
            self.popup.destroy()

        def create_dashboard_popup():
            self.popup = tk.Toplevel(self)
            self.popup.title(f'Settings Dashboard')
            self.popup.geometry("300x350")
            # Team Speaker
            tk.Label(self.popup, text="Team Speaker: ").grid(row=0, column=0, padx=10, pady=10)
            ts_entry = tk.Entry(self.popup)
            ts_entry.grid(row=0, column=1, padx=10, pady=10)
            # Line Operators
            tk.Label(self.popup, text="Line Operators: ").grid(row=1, column=0, padx=10, pady=10)
            ops_entry = tk.Entry(self.popup)
            ops_entry.grid(row=1, column=1, padx=10, pady=10)
            # Present Operators
            tk.Label(self.popup, text="Present Operators").grid(row=2, column=0, padx=10, pady=10)
            pops_entry = tk.Entry(self.popup)
            pops_entry.grid(row=2, column=1, padx=10, pady=10)
            # Shift Target
            tk.Label(self.popup, text="Shift Target:").grid(row=3, column=0, padx=10, pady=10)
            st_entry = tk.Entry(self.popup)
            st_entry.grid(row=3, column=1, padx=10, pady=10)
            # Target Per Hour
            tk.Label(self.popup, text="Target/Hour:").grid(row=4, column=0, padx=10, pady=10)
            ht_entry = tk.Entry(self.popup)
            ht_entry.grid(row=4, column=1, padx=10, pady=10)
            # Effecience
            tk.Label(self.popup, text="Effecience:").grid(row=5, column=0, padx=10, pady=10)
            eff_entry = tk.Entry(self.popup)
            eff_entry.grid(row=5, column=1, padx=10, pady=10)
            
            # Button frame to pack buttons neatly side by side
            button_frame = tk.Frame(self.popup)
            button_frame.grid(row=6, columnspan=2, pady=15)

            submit_btn = tk.Button(button_frame,
                                    text="Update",
                                    command=lambda: set_config(ts_entry.get(),
                                                               ops_entry.get(),
                                                               pops_entry.get(),
                                                               st_entry.get(),
                                                               ht_entry.get(),
                                                               eff_entry.get()),
                                    width=10,
                                    bg="#4CAF50", fg="white")
            submit_btn.grid(row=0, column=0, padx=5)

            cancel_btn = tk.Button(button_frame, text="Cancel", command=partial(cancel), width=10, bg="#f44336", fg="white")
            cancel_btn.grid(row=0, column=1, padx=5)

            self.popup.grab_set()
            self.popup.transient(self)
            self.popup.wait_window(self.popup)
        # MENU Label
        menu_label = tk.Label(self, text="MENU", bg="#002147", fg="white", font=("Arial", 20, "bold"))
        menu_label.pack(pady=(10, 0))

        # Orange Line under MENU (like in the image)
        line = tk.Frame(self, bg="#f57c00", height=4)  # Adjust height as needed
        line.pack(fill="x", padx=10, pady=(5, 20))
                
        # Load icons (resize to fit nicely)
        self.home_icon = ImageTk.PhotoImage(Image.open("./icons/home.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.data_icon = ImageTk.PhotoImage(Image.open("./icons/data.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.edit_icon = ImageTk.PhotoImage(Image.open("./icons/search.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.settings_icon = ImageTk.PhotoImage(Image.open("./icons/settings.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.dashboard_icon = ImageTk.PhotoImage(Image.open("./icons/dashboard.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.out_icon = ImageTk.PhotoImage(Image.open("./icons/loginout.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.exit_icon = ImageTk.PhotoImage(Image.open("./icons/exit.png").resize((24, 24), Image.Resampling.LANCZOS))


        # Text button
        home_btn = tk.Button(self, text="  Home", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command("home"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.home_icon, compound="left", anchor="w")
        home_btn.pack(side="top", fill="x", pady=(10, 0))
        data_btn = tk.Button(self, text="  Data", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command("edit"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.data_icon, compound="left", anchor="w")
        data_btn.pack(side="top", fill="x", pady=(10, 0))
        edit_btn = tk.Button(self, text="  Edit", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command("edit"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.edit_icon, compound="left", anchor="w")
        edit_btn.pack(side="top", fill="x", pady=(10, 0))
        settings_btn = tk.Button(self, text="  Settings", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=command("settings"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.settings_icon, compound="left", anchor="w")
        settings_btn.pack(side="top", fill="x", pady=(10, 0))
        dashboard_btn = tk.Button(self, text="  Dashboard", bg="#0a2740", fg="#f57c00",
                        font=("Arial", 14, "bold"), relief="flat", command=lambda: command("dashboard"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.dashboard_icon, compound="left", anchor="w")
        dashboard_btn.pack(side="top", fill="x", pady=(10, 0))
        
        
        
        
        

        out_btn = tk.Button(self, text="  Login OUT", bg="#e60000", fg="white",
                        font=("Arial", 10, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.out_icon, compound="left", anchor="w")
        out_btn.pack(side="bottom", fill="x", pady=(10, 0))
        exit_btn = tk.Button(self, text="  Login OUT", bg="white", fg="black",
                        font=("Arial", 10, "bold"), relief="flat", command=command,
                        activebackground="#10385c", activeforeground="#ffa726", image=self.exit_icon, compound="left", anchor="w")
        exit_btn.pack(side="bottom", fill="x", pady=(10, 0))
