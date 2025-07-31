#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import datetime

class Header(tk.Frame):
    def __init__(self, parent, app_type, user_infos):
        super().__init__(parent, bg="#ff7900", height=60)
        self.app_type = app_type
        self.user_infos = user_infos
        self.pack(side="top", fill="x")
        self.create_widgets()

    def create_widgets(self):
        print(f"Creating header for app type: {self.app_type}")
        if self.app_type == "orders_manager":
            self.title_icon = ImageTk.PhotoImage(Image.open("./icons/planner.png").resize((40, 40), Image.Resampling.LANCZOS))
            title = tk.Label(self, text="  Production Planner", bg="#ff7900", fg="navy", font=("Helvetica", 20, "bold"),image=self.title_icon, compound="left", anchor="w")
            title.pack(side="left", fill="x", padx=20)
        elif self.app_type == "picking":
            self.title_icon = ImageTk.PhotoImage(Image.open("./icons/picking.png").resize((40, 40), Image.Resampling.LANCZOS))
            title = tk.Label(self, text="  Production Picking", bg="#ff7900", fg="navy", font=("Helvetica", 20, "bold"),image=self.title_icon, compound="left", anchor="w")
            title.pack(side="left", fill="x", padx=20)
        elif self.app_type == "packaging":
            self.title_icon = ImageTk.PhotoImage(Image.open("./icons/packaging.png").resize((40, 40), Image.Resampling.LANCZOS))
            title = tk.Label(self, text="  Production Packaging", bg="#ff7900", fg="navy", font=("Helvetica", 20, "bold"),image=self.title_icon, compound="left", anchor="w")
            title.pack(side="left", fill="x", padx=20)
        
        # Container frame (orange background)
        container = tk.Frame(self, bg="#ff7900")
        container.pack(side="right", padx=20, pady=20)

        # Vertical blue stripe (narrow frame)
        blue_strip = tk.Frame(container, bg="#0a2740", width=5)
        blue_strip.pack(side="left", fill="y")

        # User info text (white, right-aligned)
        date_now = datetime.datetime.now().strftime("%d/%m/%Y")
        user_name = self.user_infos.get("username", "Guest")
        user_role = self.user_infos.get("role", "User")
        user_text = (
            f"{date_now}\n"
            f"User : {user_name}\n"
            f"Role : {user_role}"
        )

        user_info = tk.Label(
            container,
            text=user_text,
            bg="#ff7900",
            fg="white",
            justify="left",         # Align left inside the text block
            anchor="w",             # Align text to the left edge of label
            font=("Arial", 13, "bold"),
            padx=10,                # Padding between text and blue strip
        )
        user_info.pack(side="left", fill="both", expand=True)
