#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class Prodbar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#909192", height=100)
        self.pack(side="top", fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        
        project_label = tk.Label(self, text=f"Project : P2JO", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        project_label.pack(side="left", padx=(0, 0), fill="both", expand=True)
        separator = tk.Label(self, text="•", font=("Arial", 18, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        famille_label = tk.Label(self, text=f"Famille : PPL", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        famille_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self, text="•", font=("Arial", 18, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        line_label = tk.Label(self, text=f"Line : L220", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        line_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self, text="•", font=("Arial", 18, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        shift_label = tk.Label(self, text=f"Shift : 06h--14h", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        shift_label.pack(side="left", padx=(10, 0), fill="both", expand=True)