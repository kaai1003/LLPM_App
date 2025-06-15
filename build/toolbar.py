#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from functools import partial


class Toolbar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa", height=40)
        self.pack(side="top", fill="x")
        self.new_icon = ImageTk.PhotoImage(Image.open("./icons/new.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.view_icon = ImageTk.PhotoImage(Image.open("./icons/view.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.edit_icon = ImageTk.PhotoImage(Image.open("./icons/edit.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.delete_icon = ImageTk.PhotoImage(Image.open("./icons/delete.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.create_widgets()

    def create_widgets(self):
        
        def submit():
            print("submit Job")
            self.popup.destroy()
        
        def cancel():
            print("cancel Job")
            self.popup.destroy()
        
        def command(btn):
            print(f'{btn} button clicked')
            if btn == "New":
                self.popup = tk.Toplevel(self)
                self.popup.title("New Job Creation")
                self.popup.geometry("300x200")
                # Reference Input
                tk.Label(self.popup, text="Reference Input:").pack(pady=(10, 0))
                ref_entry = tk.Entry(self.popup)
                ref_entry.pack()

                # Quantity to Produce
                tk.Label(self.popup, text="Quantity to Produce:").pack(pady=(10, 0))
                qty_entry = tk.Entry(self.popup)
                qty_entry.pack()

                # Order of the Job
                tk.Label(self.popup, text="Order of the Job:").pack(pady=(10, 0))
                order_entry = tk.Entry(self.popup)
                order_entry.pack()
                
                # Button frame to pack buttons neatly side by side
                button_frame = tk.Frame(self.popup)
                button_frame.pack(pady=15)

                submit_btn = tk.Button(button_frame, text="Submit", command=submit, width=10)
                submit_btn.pack(side="left", padx=5)

                cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel, width=10)
                cancel_btn.pack(side="left", padx=5)
        
        new_btn = tk.Button(self, text="  New Job", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "New"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.new_icon, compound="left", anchor="w")
        new_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))
        # Add a separator
        separator_1 = ttk.Separator(self, orient="vertical", style="TSeparator")
        separator_1.pack(side="left", fill="y", padx=(0, 0), pady=(0, 0))
        
        view_btn = tk.Button(self, text="  View Jobs", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "View"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.view_icon, compound="left", anchor="w")
        view_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))
        # Add a separator
        separator_2 = ttk.Separator(self, orient="vertical")
        separator_2.pack(side="left", fill="y", padx=(0, 0), pady=(0, 0))
        
        edit_btn = tk.Button(self, text="  Edit Job", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "Edit"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.edit_icon, compound="left", anchor="w")
        edit_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))
        # Add a separator
        separator_3 = ttk.Separator(self, orient="vertical")
        separator_3.pack(side="left", fill="y", padx=(0, 0), pady=(0, 0))
        
        delete_btn = tk.Button(self, text="  Delete Job", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "Delete"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.delete_icon, compound="left", anchor="w")
        delete_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))