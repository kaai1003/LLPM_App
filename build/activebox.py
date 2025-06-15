#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class Activebox(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0CC506", height=100)
        self.pack(side="top", fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        
        box_label = tk.Label(self, text=f"Box : 12345678", font=("Arial", 14, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        box_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self, text="•••", font=("Arial", 14, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        ref_label = tk.Label(self, text=f"Reference : 123456 02", font=("Arial", 14, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        ref_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self, text="•••", font=("Arial", 14, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        qt_label = tk.Label(self, text=f"Quantite Total : 50", font=("Arial", 14, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        qt_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self, text="•••", font=("Arial", 14, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        packed_label = tk.Label(self, text=f"Packed : 03", font=("Arial", 14, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        packed_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self, text="•••", font=("Arial", 14, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        remain_label = tk.Label(self, text=f"Reste : 47", font=("Arial", 14, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        remain_label.pack(side="left", padx=(10, 0), fill="both", expand=True)