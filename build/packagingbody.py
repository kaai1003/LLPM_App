import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PackagingBody(tk.Frame):
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
        self.top_frame = tk.Frame(self, bg="white")
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.rowconfigure((0, 1), weight=1)
        
        self.message_label = tk.Label(
            self.top_frame,
            text="Please Scan the barcode",
            font=("Arial", 30, "bold"),
            justify="center",
            bg="white",
            fg="#0515F8"
        )
        self.message_label.grid(row=0, column=0, pady=(10, 0), sticky='nsew')

        self.test_frame = tk.Frame(self.top_frame, bg="white")
        self.test_frame.grid(row=1, column=0, sticky='nsew')
        # production Flow
        self.prod_frame1 = tk.Frame(self.test_frame, bg="white")
        self.prod_frame1.grid(row=0, column=0, padx=25, sticky='nsew')
        self.prod_label = tk.Label(
            self.prod_frame1,
            text="Production/Hour",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#0515F8"
        )
        self.prod_label.grid(row=0, column=0, padx=10, pady=0, sticky='nsew')
        self.prod_label1 = tk.Label(
            self.prod_frame1,
            text="06h00-07h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label1.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        self.prod_label2 = tk.Label(
            self.prod_frame1,
            text="07h00-08h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label2.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')
        self.prod_label3 = tk.Label(
            self.prod_frame1,
            text="08h00-09h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label3.grid(row=3, column=0, padx=10, pady=5, sticky='nsew')
        self.prod_label4 = tk.Label(
            self.prod_frame1,
            text="09h00-10h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label4.grid(row=4, column=0, padx=10, pady=5, sticky='nsew')
        self.prod_label5 = tk.Label(
            self.prod_frame1,
            text="10h00-11h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label5.grid(row=5, column=0, padx=10, pady=5, sticky='nsew')
        self.prod_label6 = tk.Label(
            self.prod_frame1,
            text="11h00-12h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label6.grid(row=6, column=0, padx=10, pady=5, sticky='nsew')
        self.prod_label7 = tk.Label(
            self.prod_frame1,
            text="12h00-13h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label7.grid(row=7, column=0, padx=10, pady=5, sticky='nsew')
        self.prod_label8 = tk.Label(
            self.prod_frame1,
            text="13h00-14h00 ==> 12 FX",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        self.prod_label8.grid(row=8, column=0, padx=10, pady=5, sticky='nsew')
        # Image
        try:
            self.img = Image.open("./icons/QRCODE.png")
            self.img = self.img.resize((600, 350), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.img)
            self.image_label = tk.Label(self.test_frame, image=self.photo, bg="white", borderwidth=0, relief="solid")
            self.image_label.grid(row=0, column=1, pady=(10, 10), sticky='nsew')
            
            self.top_frame.bind("<Configure>", self.resize_image)
        except Exception as e:
            self.image_label = tk.Label(self.test_fram, text="Image not found", bg="white", font=("Arial", 80, "bold"), fg="red")
            self.image_label.grid(row=0, column=1, sticky='nsew')

        self.top_frame.grid_rowconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)
        # Entry Field
        self.text_entry = tk.Entry(self.top_frame, font=("Arial", 16), justify="center", bg="#e0e0e0", relief="solid", borderwidth=0)
        self.text_entry.grid(row=2, column=0, ipadx=50, ipady=5, pady=(0, 20), sticky='nsew')

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

    def resize_image(self, event):
        # Resize to match the label area
        new_width = int(event.width * 0.7)  # adjust ratio if needed
        new_height = 350  # adjust ratio if needed

        resized_img = self.img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_img)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo