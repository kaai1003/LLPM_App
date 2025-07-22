import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from models.galia import Galia
from models.scanned import Scanned
from models.engine.app_tools import picking_db_conn
from models.engine.app_tools import get_line_details
from models.engine.db_manager import set_db_conn
from models.engine.db_manager import get_connection
from models.engine.shift import get_current_shift
from models.engine.shift import working_hours
from models.engine.app_tools import get_line_id
from models.engine.db_manager import get_obj
from models.engine.packaging_manager import check_packaging_config
from models.engine.packaging_manager import check_box_ref
from PIL import Image, ImageTk

class PackagingBody(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
         # load database settings
        db_settings = picking_db_conn()
        if get_connection(db_settings) is None:
            print("Error Connecting to Database")
            messagebox.showerror("Error Connecting to Database.", 
                                 "Please check your database settings in the config file.")
            exit(1)
        print(db_settings)
        set_db_conn(db_settings)
        self.init_vars()
        self.activebox_vars()
        self.create_widgets()
            
    def create_widgets(self):
        # get production lin details
        
        line_id = get_line_id()
        if not line_id:
            messagebox.showerror("Error", "Line ID not found in settings.")
            return
        print(f"Line ID: {line_id}")
        line_details = get_line_details(line_id)
        if not line_details:
            messagebox.showerror("Error", f"Line {line_id} not found in configuration.")
            return
        project = line_details.get("project", "Unknown")
        famille = line_details.get("famille", "Unknown")
        line = line_details.get("line_id", "Unknown")
        try:
            shift_name, shift_range = get_current_shift()
            if shift_name:
                print(f"✅ Current time is within {shift_name} ({shift_range})")
            else:
                print("⚠️ Current time does not match any shift.")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # ================
        # Packaging Process====>
        # ================

        def packaging_scan(event):
            """Handle the packaging scan event"""
            input = self.text_entry.get().strip()
            print(input)
            if not input or input == "":
                return
            if input == "NEW_BOX":
                # Reset active box variables
                self.init_vars()
                self.activebox_vars()
                self.create_widgets()
                self.text_entry.delete(0, tk.END)
                return
            if self.scan_step == "BOX":
                if self.barcode_specs["barcode"] == "reference":
                    print(self.barcode_prefix)
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    self.box_ref = self.box_ref[len(self.barcode_prefix):]
                    ref_obj = get_obj("reference", "ref", self.box_ref)
                    if not ref_obj:
                        messagebox.showerror("Error", f"Reference {self.box_ref} not found in database.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    self.opned_box_ref = check_box_ref(self.box_ref)
                    self.step_num += 1
                    self.barcode_specs = self.box_config[self.step_num + 1]
                    self.barcode_prefix = self.barcode_specs["prefix"]
                    self.barcode_img = self.barcode_specs.get("photo", self.not_found)
                    self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
                    self.create_widgets()
                    return
                elif self.barcode_specs["barcode"] == "nrgalia":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    nr_galia = input[len(self.barcode_prefix):]
                    if self.opned_box_ref:
                        if self.opened_box_ref["nr_galia"] != nr_galia:
                            messagebox.showerror("Error", f"NR Galia {nr_galia} does not match opened box reference.")
                            self.init_vars()
                            self.activebox_vars()
                            self.create_widgets()
                            self.text_entry.delete(0, tk.END)
                            return
                        self.status_galia = "open"
                        self.current_galia = Galia(**self.opned_box_ref)
                        print(f"Galia {nr_galia} is Opened and {self.opned_box_ref['scanned_q']} Fx Scanned")
                     # check if nrgalia exist in Database
                    galia_obj = get_obj("galia", "nr_galia", nr_galia)
                    if galia_obj is None:
                        self.status_galia = "new"
                        self.current_galia = Galia()
                        self.current_galia.nr_galia = nr_galia
                        self.current_galia.reference = self.box_ref
                        self.current_galia.line_id = line_id
                        print(f"New Galia {nr_galia} Scanned")
                    elif galia_obj["status"] == "closed":
                        status_galia = "closed"
                        print(f"Galia {nr_galia[len(self.barcode_prefix):]} is Already Closed")
                    elif galia_obj["status"] == "open":
                        print(f"---Error!!!!---: Galia {nr_galia} is Already Opened with Different Reference {galia_obj['reference']}")
                        print("Please Check the Scanned Galia!!!")
                    
        # Configure row weights: 3/4 for top content, 1/4 for table
        self.rowconfigure(0, weight=0)  # prodbar
        self.rowconfigure(1, weight=0)  # activebox
        self.rowconfigure(2, weight=6)  # top_frame (barcode + image)
        self.rowconfigure(3, weight=2)  # footer (table)
        self.columnconfigure(0, weight=1)

        # ======================
        # Production Line informations
        # ======================
        self.prodbar = tk.Frame(self, bg="#909192")
        self.prodbar.columnconfigure(0, weight=0)
        self.prodbar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        # Create labels for project, family, line, and shift
        # ======================
        project_label = tk.Label(self.prodbar, text=f"Project : {project}", font=("Arial", 30, "bold"),
                         bg="#909192", fg="white")
        project_label.pack(side="left", padx=(0, 0), fill="both", expand=True)
        separator = tk.Label(self.prodbar, text="•", font=("Arial", 30, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=0, fill="both", expand=True)
        famille_label = tk.Label(self.prodbar, text=f"Famille : {famille}", font=("Arial", 30, "bold"),
                         bg="#909192", fg="white")
        famille_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.prodbar, text="•", font=("Arial", 30, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        line_label = tk.Label(self.prodbar, text=f"Line : {line}", font=("Arial", 30, "bold"),
                         bg="#909192", fg="white")
        line_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.prodbar, text="•", font=("Arial", 30, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        shift_label = tk.Label(self.prodbar, text=f"Shift : {shift_range}", font=("Arial", 30, "bold"),
                         bg="#909192", fg="white")
        shift_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        
        # ======================
        # Active Picking Reference
        # ======================
        self.activebox = tk.Frame(self, bg="#0CC506", height=100)
        self.activebox.grid(row=1, column=0, sticky="ew")
        self.activebox.columnconfigure(0, weight=1)
        
        box_label = tk.Label(self.activebox, text=f"Box : {self.box_number}", font=("Arial", 22, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        box_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.activebox, text="•••", font=("Arial", 22, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        ref_label = tk.Label(self.activebox, text=f"Reference : {self.box_ref}", font=("Arial", 22, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        ref_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.activebox, text="•••", font=("Arial", 22, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        qt_label = tk.Label(self.activebox, text=f"Quantite Total : {self.box_q}", font=("Arial", 22, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        qt_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.activebox, text="•••", font=("Arial", 22, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        packed_label = tk.Label(self.activebox, text=f"Packed : {self.box_p}", font=("Arial", 22, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        packed_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.activebox, text="•••", font=("Arial", 22, "bold"),
                             bg="#0CC506", fg="white")
        separator.pack(side="left", padx=5, fill="both", expand=True)
        remain_label = tk.Label(self.activebox, text=f"Reste : {self.box_r}", font=("Arial", 22, "bold"),
                         bg="#0CC506", fg="#0D0D0E")
        remain_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        # ======================
        # Middle Frame (Message + Image + Entry)
        # ======================
        self.top_frame = tk.Frame(self, bg="blue")
        self.top_frame.grid(row=2, column=0, sticky="nsew")
        self.top_frame.rowconfigure(0, weight=0)  # message_label
        self.top_frame.rowconfigure(1, weight=4, minsize=300)  # test_frame (main visual content)
        self.top_frame.rowconfigure(2, weight=0)  # entry
        self.top_frame.columnconfigure(0, weight=1)
        
        # message
        self.message_label = tk.Label(
            self.top_frame,
            text=f"Please Scan {self.scan_msg} barcode",
            font=("Arial", 50, "bold"),
            justify="center",
            bg="white",
            fg="#F80505",
        )
        self.message_label.grid(row=0, column=0, pady=(0, 0), sticky='nsew')

        self.test_frame = tk.Frame(self.top_frame, bg="green", height=350)
        self.test_frame.grid(row=1, column=0, sticky='nsew')
        self.test_frame.rowconfigure(0, weight=1)
        self.test_frame.columnconfigure(0, weight=1)  # prod_frame1
        self.test_frame.columnconfigure(1, weight=6)  # image frame (larger portion)
        # production Flow
        self.prod_frame1 = tk.Frame(self.test_frame, bg="gray")
        self.prod_frame1.grid(row=0, column=0, padx=0, sticky='nsew')
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
        
        # Image Frame
        self.imgframe = tk.Frame(self.test_frame, bg="black")
        self.imgframe.grid(row=0, column=1, padx=0, sticky='nsew')
        self.imgframe.rowconfigure(0, weight=0)
        self.img_canvas = tk.Canvas(self.imgframe, bg="#F30A0A", highlightthickness=0)
        self.img_canvas.pack(fill=tk.BOTH, expand=True)
        try:
            self.img = Image.open(self.barcode_img)
            self.photo = ImageTk.PhotoImage(self.img)
            self.image_id = self.img_canvas.create_image(0, 0, anchor='nw', image=self.photo)
            
        except Exception as e:
            self.img = Image.open(self.not_found)
            self.photo = ImageTk.PhotoImage(self.img)
            self.image_id = self.img_canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.img_canvas.bind("<Configure>", self.resize_image)
        # Entry Field
        self.text_entry = tk.Entry(self.top_frame, font=("Arial", 16), justify="center", bg="#e0e0e0", relief="solid", borderwidth=0)
        self.text_entry.grid(row=2, column=0, ipadx=50, ipady=5, pady=(0, 0), sticky='nsew')
        self.text_entry.focus_set()
        self.text_entry.bind("<Return>", packaging_scan)
        self.bind("<Button-1>", lambda e: self.text_entry.focus_set())

        # ======================
        # Footer Frame (Table)
        # ======================
        footer = tk.Frame(self, bg="#f0f0f0")
        footer.grid(row=3, column=0, sticky="nsew")
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
        # Resize image to the exact size of the canvas
        new_width = event.width
        new_height = event.height

        resized = self.img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized)

        # Update canvas image
        self.img_canvas.itemconfig(self.image_id, image=self.photo)
        self.img_canvas.image = self.photo  # Prevent garbage collection

        # Position at top-left corner (fills canvas)
        self.img_canvas.coords(self.image_id, 0, 0)
    
    def init_vars(self):
        # Initialize variables or settings if needed
        self.step_num = 0
        self.not_found = "./app_images/not_found.jpg"
        self.packing_config = check_packaging_config()
        if not self.packing_config:
            messagebox.showerror("Error", "Packaging configuration not found.")
            exit(1)
        print(f"Packaging configuration: {self.packing_config}")    
        self.box_config = self.packing_config.get("BOX", None)
        if not self.box_config:
            messagebox.showerror("Error", "Box configuration not found in packaging settings.")
            exit(1)
        self.scan_step = "BOX"
        self.box_barcode_count = len(self.box_config)
        if self.box_barcode_count < 3:
            messagebox.showerror("Error", "Box configuration must have at least 3 steps.")
            exit(1)
        self.barcode_specs = self.box_config[self.step_num]
        self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
        self.barcode_prefix = self.barcode_specs["prefix"]
        self.barcode_img = self.barcode_specs.get("photo", self.not_found)
        self.box_ref = ""
        self.box_number = ""
        self.box_q = 0
        self.opened_box_ref = None
        self.status_galia = None
        self.current_galia = None
        self.horking_hours = working_hours()

    def activebox_vars(self):
        # Initialize active box variables
        self.box_number = ""
        self.box_ref = ""
        self.box_q = 0
        self.box_p = 0
        self.box_r = 0
