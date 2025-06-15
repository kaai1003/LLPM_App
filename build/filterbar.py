#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
from PIL import Image, ImageTk
from models.engine.app_tools import load_lines
from build.plannerbody import PlannerBody
from functools import partial


class FilterBar(tk.Frame):
    def __init__(self, parent, plannerbody):
        super().__init__(parent, bg="#e6f2ff")
        self.plannerbody = plannerbody
        self.pack(fill="x", padx=0, pady=0)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Jobs Filter", bg="#e6f2ff", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        fields = ["Line ID", "Reference", "Status Job", "Date"]
        self.entries = {}

        # Define dropdown options
        line_ids = load_lines()
        status_options = ["pending", "paused", "closed"]
        today = datetime.today()
        for idx, field in enumerate(fields):
            tk.Label(self, text=field, bg="#e6f2ff").grid(row=1, column=idx * 2, padx=5, pady=5)

            if field == "Line ID":
                entry = ttk.Combobox(self, values=line_ids, state="readonly")
            elif field == "Status Job":
                entry = ttk.Combobox(self, values=status_options, state="readonly")
            elif field == "Date":
                entry = DateEntry(self,
                                  width=12,
                                  background="darkblue",
                                  foreground="white",
                                  borderwidth=2,
                                  date_pattern='yyyy-MM-dd',
                                  year=today.year,
                                  month=today.month,
                                  day=today.day)
            else:  # Reference remains a regular Entry
                entry = tk.Entry(self)

            entry.grid(row=1, column=idx * 2 + 1, padx=5, pady=5)
            self.entries[field] = entry

        tk.Button(self, text="Search", bg="orange", fg="white", font=("Arial", 10, "bold"), command=partial(self.search)).grid(row=1, column=8, padx=10)

    def search(self):
        filter_values = {k: e.get() for k, e in self.entries.items()}
        print("Search clicked. Values:", filter_values)
        self.plannerbody.filter_jobs(
            line_id=filter_values["Line ID"],
            reference=filter_values["Reference"],
            status=filter_values["Status Job"],
            date=filter_values["Date"]
        )
        
