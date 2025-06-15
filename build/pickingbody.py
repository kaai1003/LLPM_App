import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PickingBody(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Configure row weights: 3/4 for top content, 1/4 for table
        self.rowconfigure(0, weight=3)  # Top content
        self.rowconfigure(1, weight=1)  # Table
        self.columnconfigure(0, weight=1)

        # ======================
        # Top Frame (Image + Entry)
        # ======================
        top_frame = tk.Frame(self, bg="white")
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.columnconfigure(0, weight=1)
        top_frame.rowconfigure((0, 1), weight=1)
        
        self.message_label = tk.Label(
            top_frame,
            text="Please Press Enter Key",
            font=("Arial", 30, "bold"),
            justify="center",
            bg="white",
            fg="#0515F8"
        )
        self.message_label.grid(row=0, column=0, pady=(10, 0))

        # Image
        try:
            img = Image.open("../icons/computer-enter-key-finger-pressing-260nw-272983391.webp")
            img = img.resize((400, 200), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            image_label = tk.Label(top_frame, image=self.photo, bg="white", borderwidth=1, relief="solid")
            image_label.grid(row=1, column=0, pady=(20, 10))
        except Exception as e:
            image_label = tk.Label(top_frame, text="Image not found", bg="white")
            image_label.grid(row=1, column=0)

        # Entry Field
        self.text_entry = tk.Entry(top_frame, font=("Arial", 16), justify="center", bg="#e0e0e0", relief="solid")
        self.text_entry.grid(row=2, column=0, ipadx=50, ipady=5, pady=(0, 20))

        # ======================
        # Footer Frame (Table)
        # ======================
        footer = tk.Frame(self, bg="#f0f0f0")
        footer.grid(row=1, column=0, sticky="nsew")
        footer.columnconfigure(0, weight=1)
        footer.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            footer,
            columns=("line", "reference", "status"),
            show="headings",
            height=5
        )
        self.tree.heading("line", text="Line ID")
        self.tree.heading("reference", text="Reference")
        self.tree.heading("status", text="Status Job")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(footer, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Sample Data
        jobs = [
            ("L1", "REF001", "Running"),
            ("L2", "REF002", "Stopped"),
            ("L3", "REF003", "Waiting"),
        ]
        for job in jobs:
            self.tree.insert("", "end", values=job)
