#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class Activeref(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0CC506", height=100)
        self.pack(side="top", fill="x")
        self.create_widgets()

    def create_widgets(self):
        
        project_label = tk.Label(self, text=f"Reference : 123456 02", font=("Arial", 18, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        project_label.pack(side="left", padx=(10, 0))
        separator = tk.Label(self, text="•••", font=("Arial", 18, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=10)
        famille_label = tk.Label(self, text=f"Quantite Total : 50", font=("Arial", 18, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        famille_label.pack(side="left", padx=(10, 0))
        separator = tk.Label(self, text="•••", font=("Arial", 18, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=10)
        line_label = tk.Label(self, text=f"Picked : 03", font=("Arial", 18, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        line_label.pack(side="left", padx=(10, 0))
        separator = tk.Label(self, text="•••", font=("Arial", 18, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=10)
        shift_label = tk.Label(self, text=f"Reste : 47", font=("Arial", 18, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        shift_label.pack(side="left", padx=(10, 0))