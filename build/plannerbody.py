#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from functools import partial
from datetime import datetime
from models.engine.job_manager import get_all_jobs
from models.engine.app_tools import load_lines
from models.engine.job_manager import create_job
from models.engine.job_manager import jobs_by_line
from models.engine.db_manager import get_connection
from models.engine.db_manager import set_db_conn
from models.engine.app_tools import get_line_conn

class PlannerBody(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.new_icon = ImageTk.PhotoImage(Image.open("./icons/new.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.view_icon = ImageTk.PhotoImage(Image.open("./icons/view.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.edit_icon = ImageTk.PhotoImage(Image.open("./icons/edit.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.delete_icon = ImageTk.PhotoImage(Image.open("./icons/delete.png").resize((24, 24), Image.Resampling.LANCZOS))
        self.create_widgets()

    def create_widgets(self):
        # Configure grid layout
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=2)  # Data table area
        self.rowconfigure(3, weight=7)  # Footer with graphs
        self.columnconfigure(0, weight=1)
        # -----------------------
        # Tool Bar (top section)
        # -----------------------
        self.toolbar = tk.Frame(self, bg="#f8f9fa", height=40)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        #self.toolbar.columnconfigure((0, 1, 2, 3), weight=1)
        def submit(line_id, ref, qt, order):
            new_job = create_job(ref, line_id, qt, order)
            if new_job is None:
                tk.Label(self.popup, text="Error creating job. Please try again.", fg="red").pack(pady=10)
                return
            tk.Label(self.popup, text=f'Job created successfully!\n{new_job}', fg="green").pack(pady=10)
            self.tree.delete(*self.tree.get_children())
            self.jobs = get_all_jobs()
            for job in self.jobs:
                self.tree.insert("", "end", values=job)
            print("submit Job")
        
        def cancel():
            print("cancel Job")
            self.popup.destroy()

        def create_job_popup():
            self.popup = tk.Toplevel(self.toolbar)
            self.popup.title("New Job Creation")
            self.popup.geometry("600x300")
            # lines Selection
            tk.Label(self.popup, text="Select Line:").pack(pady=(10, 0))
            line_combobox = ttk.Combobox(self.popup, values=load_lines(), state="readonly")
            line_combobox.pack()
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

            submit_btn = tk.Button(button_frame,
                                    text="Submit",
                                    command=lambda: submit(
                                        line_combobox.get(), ref_entry.get(), qty_entry.get(), order_entry.get()
                                        ),
                                    width=10)
            submit_btn.pack(side="left", padx=5)

            cancel_btn = tk.Button(button_frame, text="Cancel", command=partial(cancel), width=10)
            cancel_btn.pack(side="left", padx=5)
        def command(btn):
            print(f'{btn} button clicked')
            if btn == "New":
                create_job_popup()
            elif btn == "View":
                self.tree.delete(*self.tree.get_children())
                self.jobs = get_all_jobs()
                for job in self.jobs:
                    self.tree.insert("", "end", values=job)
        def search():
            filter_values = {k: e.get() for k, e in self.entries.items()}
            print("Search clicked. Values:", filter_values)
            self.filter_jobs(
                line_id=filter_values["Line ID"],
                reference=filter_values["Reference"],
                status=filter_values["Status Job"],
                date=filter_values["Date"]
            )
        new_btn = tk.Button(self.toolbar, text="  New Job", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "New"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.new_icon, compound="left", anchor="w")
        new_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))
        # Add a separator
        separator_1 = ttk.Separator(self.toolbar, orient="vertical", style="TSeparator")
        separator_1.pack(side="left", fill="y", padx=(0, 0), pady=(0, 0))
        
        view_btn = tk.Button(self.toolbar, text="  View Jobs", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "View"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.view_icon, compound="left", anchor="w")
        view_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))
        # Add a separator
        separator_2 = ttk.Separator(self.toolbar, orient="vertical")
        separator_2.pack(side="left", fill="y", padx=(0, 0), pady=(0, 0))
        
        edit_btn = tk.Button(self.toolbar, text="  Edit Job", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "Edit"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.edit_icon, compound="left", anchor="w")
        edit_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))
        # Add a separator
        separator_3 = ttk.Separator(self.toolbar, orient="vertical")
        separator_3.pack(side="left", fill="y", padx=(0, 0), pady=(0, 0))
        
        delete_btn = tk.Button(self.toolbar, text="  Delete Job", bg="#9b9c9c", fg="#0c0c0c",
                        font=("Arial", 10), relief="flat", command=partial(command, "Delete"),
                        activebackground="#10385c", activeforeground="#ffa726", image=self.delete_icon, compound="left", anchor="w")
        delete_btn.pack(side="left", fill="y", pady=(0, 0), padx=(0, 0))
        # -----------------------
        # Filter Bar (Second section)
        # -----------------------
        self.filterbar = tk.Frame(self, bg="#e6f2ff")
        self.filterbar.grid(row=1, column=0, sticky="ew")
        tk.Label(self.filterbar, text="Jobs Filter", bg="#e6f2ff", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        fields = ["Line ID", "Reference", "Status Job", "Date"]
        self.entries = {}

        # Define dropdown options
        line_ids = load_lines()
        status_options = ["pending", "paused", "closed"]
        today = datetime.today()
        for idx, field in enumerate(fields):
            tk.Label(self.filterbar, text=field, bg="#e6f2ff").grid(row=1, column=idx * 2, padx=5, pady=5)

            if field == "Line ID":
                entry = ttk.Combobox(self.filterbar, values=line_ids, state="readonly")
            elif field == "Status Job":
                entry = ttk.Combobox(self.filterbar, values=status_options, state="readonly")
            elif field == "Date":
                entry = DateEntry(self.filterbar,
                                  width=12,
                                  background="darkblue",
                                  foreground="white",
                                  borderwidth=2,
                                  date_pattern='yyyy-MM-dd',
                                  year=today.year,
                                  month=today.month,
                                  day=today.day)
            else:  # Reference remains a regular Entry
                entry = tk.Entry(self.filterbar)

            entry.grid(row=1, column=idx * 2 + 1, padx=5, pady=5)
            self.entries[field] = entry

        tk.Button(self.filterbar, text="Search", bg="orange", fg="white", font=("Arial", 10, "bold"), command=partial(search)).grid(row=1, column=8, padx=10)
        
        # -----------------------
        # Data Table (Third section)
        # -----------------------
        table_frame = tk.Frame(self, bg="white")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=3)
        table_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="#333333")
        
        self.tree = ttk.Treeview(
            table_frame, 
            columns=("ID", "reference", "line", "quantity", "picked", "remain", "status", "order", "created", "updated"), 
            show="headings"
        )
        
        # Define columns and widths
        columns = {
            "ID": 0,
            "reference": 100,
            "line": 80,
            "quantity": 80,
            "picked": 80,
            "remain": 80,
            "status": 100,
            "order": 100,
            "created": 130,
            "updated": 130
        }

        for col, width in columns.items():
            if col == "ID":
                self.tree.heading(col, text="")
                self.tree.column(col, width=width, anchor="center")
            else:
                self.tree.heading(col, text=col.capitalize())
                self.tree.column(col, width=width, anchor="center")  # or anchor="w" for left-align
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        #data
        self.jobs = get_all_jobs()
        for job in self.jobs:
            self.tree.insert("", "end", values=job)
        # -----------------------
        # Footer (graph section)
        # -----------------------
        footer = tk.Frame(self, bg="#e4dcdc")
        footer.grid(row=3, column=0, sticky="nsew")
        footer.columnconfigure((0, 1, 2), weight=2)
        footer.rowconfigure(0, weight=1)

        for i in range(3):
            graph = tk.Frame(footer, bg="#cccccc", bd=2, relief="groove")
            graph.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            tk.Label(graph, text=f"Graph {i+1}", bg="#cccccc", font=("Arial", 10, "bold")).pack(pady=10)

    def filter_jobs(self, line_id, reference, status, date):
        filters = {
            2: line_id,
            1: reference,
            6: status,
            8: date
        }

        def match(job):
            for index, value in filters.items():
                if value and (
                    (index == 8 and job[index].strftime('%Y-%m-%d') != value)
                    or (index != 8 and job[index] != value)
                ):
                    return False
            return True

        self.tree.delete(*self.tree.get_children())
        filtered_jobs = [job for job in self.jobs if match(job)]

        for job in filtered_jobs:
            self.tree.insert("", "end", values=job)
