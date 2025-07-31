import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
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
from models.engine.packaging_manager import check_cpt_hns
from models.engine.packaging_manager import list_hns_labels
from models.engine.printer import tsc_label
from PIL import Image, ImageTk

class PackagingBody(tk.Frame):
    def __init__(self, parent, user_infos):
        super().__init__(parent, bg="white")
        self.user_infos = user_infos
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
        self.packing_config = check_packaging_config()
        if not self.packing_config:
            messagebox.showerror("Error", "Packaging configuration not found.")
            exit(1)
        print(f"Packaging configuration: {self.packing_config}")
        self.scan_config = None
        self.barcode_specs = None
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
            messagebox.showerror("Error", f"Line {line_id} not found in Database.")
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
                    self.box_ref = input[len(self.barcode_prefix):]
                    print(f"Box Reference Scanned: {self.box_ref}")
                    ref_obj = get_obj("reference", "ref", self.box_ref)
                    if not ref_obj:
                        messagebox.showerror("Error", f"Reference {self.box_ref} not found in database.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    self.opened_box_ref = check_box_ref(self.box_ref)
                    self.next_step()
                    return
                elif self.barcode_specs["barcode"] == "nrgalia":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    nr_galia = input[len(self.barcode_prefix):]
                    if self.opened_box_ref and self.opened_box_ref["line_id"] == line_id:
                        print(f"Opened Box Reference: {self.opened_box_ref}")
                        if self.opened_box_ref["nr_galia"] != nr_galia:
                            messagebox.showerror("Error", f"NR Galia {nr_galia} does not match opened box reference.")
                            self.init_vars()
                            self.activebox_vars()
                            self.create_widgets()
                            self.text_entry.delete(0, tk.END)
                            return
                        self.current_galia = Galia(**self.opened_box_ref)
                        self.status_galia = self.opened_box_ref["status"]
                        print(f"Galia {nr_galia} is Opened and {self.opened_box_ref['scanned_q']} Fx Scanned")
                        self.next_step()
                        return
                     # check if nrgalia exist in Database
                    galia_obj = get_obj("galia", "nr_galia", nr_galia)
                    if galia_obj is None:
                        self.current_galia = Galia()
                        self.current_galia.status = "open"
                        self.current_galia.nr_galia = nr_galia
                        self.current_galia.reference = self.box_ref
                        self.current_galia.line_id = line_id
                        self.new_box = True
                        self.next_step()
                        print(f"New Galia {nr_galia} Scanned")
                    elif galia_obj["status"] == "closed":
                        messagebox.showerror("Error", f"Galia {nr_galia} is already closed.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        print(f"Galia {nr_galia[len(self.barcode_prefix):]} is Already Closed")
                        return
                    elif galia_obj["status"] == "open":
                        messagebox.showerror("Error", f"Galia {nr_galia} is already opened with reference {galia_obj['reference']}.")
                        print(f"---Error!!!!---: Galia {nr_galia} is Already Opened with Different Reference {galia_obj['reference']}")
                        print("Please Check the Scanned Galia!!!")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                elif self.barcode_specs["barcode"] == "quantity":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    try:
                        quantity = int(input[len(self.barcode_prefix):])
                    except ValueError:
                        messagebox.showerror("Error", "Invalid quantity scanned. Please scan a valid number.")
                        self.text_entry.delete(0, tk.END)
                        return
                    if quantity <= 0:
                        messagebox.showerror("Error", "Quantity must be greater than zero.")
                        self.text_entry.delete(0, tk.END)
                        return
                    if self.new_box == False:
                        if quantity != self.current_galia.total_q:
                            messagebox.showerror("Error", f"Scanned quantity {quantity} does not match opened Galia quantity {self.current_galia.scanned_q}.")
                            self.init_vars()
                            self.activebox_vars()
                            self.create_widgets()
                            self.text_entry.delete(0, tk.END)
                            return
                        self.text_entry.delete(0, tk.END)
                        self.current_galia.update()
                        self.next_step()
                        return
                    self.current_galia.total_q = quantity
                    self.current_galia.scanned_q = 0
                    self.current_galia.remain_q = quantity
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
                elif self.barcode_specs["barcode"] == "box_type":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    self.box_type_barcode = input[len(self.barcode_prefix):]
                    self.box_type = True
                    print(f"Box Type Scanned: {self.box_type_barcode}")
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
            elif self.scan_step == "FX":
                if self.barcode_specs["barcode"] == "reference":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    self.scanned_ref = input[len(self.barcode_prefix):]
                    print(f"FX Reference Scanned: {self.scanned_ref}")
                    if self.scanned_ref != self.current_galia.reference:
                        messagebox.showerror("Error", f"FX Reference {self.fx_ref} does not match opened Galia reference {self.current_galia.reference}.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    print(f"FX Reference Scanned: {self.fx_ref}")
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
                elif self.barcode_specs["barcode"] == "compteur":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    self.scanned_cpt = input[len(self.barcode_prefix):]
                    print(f"FX Compteur Scanned: {self.scanned_cpt}")
                    if not self.fx_cpt:
                        if check_cpt_hns(self.scanned_cpt) is False:
                            messagebox.showerror("Error", f"FX Compteur {self.scanned_cpt} already scanned.")
                            self.init_vars()
                            self.activebox_vars()
                            self.create_widgets()
                            self.text_entry.delete(0, tk.END)
                            return
                        self.fx_cpt = self.scanned_cpt
                        print(f"FX Compteur {self.fx_cpt} Scanned")
                        self.text_entry.delete(0, tk.END)
                        self.next_step()
                        return
                    if self.scanned_cpt != self.fx_cpt:
                        messagebox.showerror("Error", f"Scanned Compteur {self.scanned_cpt} does not match opened FX compteur {self.fx_cpt}.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
                elif self.barcode_specs["barcode"] == "box_type":
                    if not self.box_type:
                        messagebox.showerror("Error", "Box Type not scanned yet. Please scan Box Configurationn.")
                        self.text_entry.delete(0, tk.END)
                        return
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    self.fx_box_type = input[len(self.barcode_prefix):]
                    if self.fx_box_type != self.box_type_barcode:
                        messagebox.showerror("Error", f"Scanned Box Type {self.fx_box_type} does not match opened Box Type {self.box_type_barcode}.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    print(f"Box Type Scanned: {self.fx_box_type}")
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
            elif self.scan_step == "VALIDATION":
                if self.barcode_specs["barcode"] == "reference":
                    print(self.barcode_prefix)
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    ref_validation = input[len(self.barcode_prefix):]
                    print(f"Box Reference Scanned: {self.box_ref}")
                    if ref_validation != self.current_galia.reference:
                        messagebox.showerror("Error", f"Validation Reference {ref_validation} does not match opened Galia reference {self.current_galia.reference}.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
                elif self.barcode_specs["barcode"] == "nrgalia":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    nr_galia_validation = input[len(self.barcode_prefix):]
                    if nr_galia_validation != self.current_galia.nr_galia:
                        messagebox.showerror("Error", f"Validation NR Galia {nr_galia_validation} does not match opened Galia NR {self.current_galia.nr_galia}.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
                elif self.barcode_specs["barcode"] == "quantity":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    try:
                        quantity_validation = int(input[len(self.barcode_prefix):])
                    except ValueError:
                        messagebox.showerror("Error", "Invalid quantity scanned. Please scan a valid number.")
                        self.text_entry.delete(0, tk.END)
                        return
                    if quantity_validation <= 0:
                        messagebox.showerror("Error", "Quantity must be greater than zero.")
                        self.text_entry.delete(0, tk.END)
                        return
                    if quantity_validation != self.current_galia.total_q:
                        messagebox.showerror("Error", f"Validation quantity {quantity_validation} does not match opened Galia quantity {self.current_galia.total_q}.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
                elif self.barcode_specs["barcode"] == "box_type":
                    if not input.startswith(self.barcode_prefix):
                        messagebox.showerror("Error", f"Invalid barcode prefix. Expected: {self.barcode_prefix}")
                        self.text_entry.delete(0, tk.END)
                        return
                    box_type_validation = input[len(self.barcode_prefix):]
                    if box_type_validation != self.box_type_barcode:
                        messagebox.showerror("Error", f"Validation Box Type {box_type_validation} does not match opened Box Type {self.box_type_barcode}.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        self.text_entry.delete(0, tk.END)
                        return
                    self.text_entry.delete(0, tk.END)
                    self.next_step()
                    return
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
        # Initiate FX Step variables
        self.labels_list = []
        self.labels_count = 0
        self.label_step = 0
        self.label_barcodes = []
        self.fx_barcode_count = 0
        self.fx_label = None
        self.scanned_ref = None
        self.fx_ref = None
        self.scanned_cpt = None
        self.fx_cpt = None
        self.fx_box_type = None
        # Initialize Box Step variables
        self.new_box = False
        self.box_type_barcode = ""
        self.box_type = False
        self.scan_config = self.packing_config.get("BOX", None)
        if not self.scan_config:
            messagebox.showerror("Error", "Box configuration not found in packaging settings.")
            exit(1)
        self.scan_step = "BOX"
        self.box_barcode_count = len(self.scan_config)
        if self.box_barcode_count < 3:
            messagebox.showerror("Error", "Box configuration must have at least 3 Barcodes.")
            exit(1)
        self.barcode_specs = self.scan_config[self.step_num]
        self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
        self.barcode_prefix = self.barcode_specs["prefix"]
        self.barcode_img = self.barcode_specs.get("photo", self.not_found)
        # Current Box Variables
        self.box_ref = ""
        self.box_number = ""
        self.box_q = 0
        self.opened_box_ref = None
        self.status_galia = None
        self.current_galia = None
        self.horking_hours = working_hours()

    def activebox_set(self, box_number, box_ref, box_q, box_p, box_r):
        self.box_number = box_number
        self.box_ref = box_ref
        self.box_q = box_q
        self.box_p = box_p
        self.box_r = box_r

    def activebox_vars(self):
        # Initialize active box variables
        self.box_number = ""
        self.box_ref = ""
        self.box_q = 0
        self.box_p = 0
        self.box_r = 0

    def next_step(self):
        """Proceed to the next step in the packaging process"""
        self.step_num += 1
        if self.scan_step == "BOX":
            if self.step_num < self.box_barcode_count:
                self.barcode_specs = self.scan_config[self.step_num]
                self.barcode_prefix = self.barcode_specs["prefix"]
                self.barcode_img = self.barcode_specs.get("photo", self.not_found)
                self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
                self.create_widgets()
                return
            self.scan_config = self.packing_config.get("FX", None)
            if not self.scan_config:
                messagebox.showerror("Error", "FX configuration not found in packaging settings.")
                self.init_vars()
                self.activebox_vars()
                self.create_widgets()
                return
            self.scan_step = "FX"
            self.labels_list = list_hns_labels(self.scan_config)
            self.labels_count = len(self.labels_list)
            self.label_step = 0
            self.fx_label = self.labels_list[self.label_step]
            self.label_barcodes = self.scan_config[self.fx_label]
            self.fx_barcode_count = len(self.label_barcodes)
            if self.fx_barcode_count < 2:
                messagebox.showerror("Error", "FX configuration must have at least 2 barcode.")
                self.init_vars()
                self.activebox_vars()
                self.create_widgets()
                return
            self.current_galia.save()
            print(f"---New Galia {self.current_galia.nr_galia} Created---")
            print("-----------Box Scan Completed-------------")
            print(f"Scanned Box: {self.current_galia.to_dict()}")
            self.activebox_set(self.current_galia.nr_galia,
                               self.current_galia.reference,
                               self.current_galia.total_q,
                               self.current_galia.scanned_q,
                               self.current_galia.remain_q)
            self.step_num = 0
            self.barcode_specs = self.label_barcodes[self.step_num]
            self.barcode_prefix = self.barcode_specs["prefix"]
            self.barcode_img = self.barcode_specs.get("photo", self.not_found)
            self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
            self.create_widgets()
            return
        elif self.scan_step == "FX":
            if self.step_num < self.fx_barcode_count:
                self.barcode_specs = self.label_barcodes[self.step_num]
                self.barcode_prefix = self.barcode_specs["prefix"]
                self.barcode_img = self.barcode_specs.get("photo", self.not_found)
                self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
                self.create_widgets()
                return
            else:
                # Move to next label step
                self.label_step += 1
                if self.label_step < self.labels_count:
                    self.fx_label = self.labels_list[self.label_step]
                    self.label_barcodes = self.scan_config[self.fx_label]
                    self.fx_barcode_count = len(self.label_barcodes)
                    if self.fx_barcode_count < 2:
                        messagebox.showerror("Error", "FX configuration must have at least 2 barcode.")
                        self.init_vars()
                        self.activebox_vars()
                        self.create_widgets()
                        return
                    self.step_num = 0
                    self.barcode_specs = self.label_barcodes[self.step_num]
                    self.barcode_prefix = self.barcode_specs["prefix"]
                    self.barcode_img = self.barcode_specs.get("photo", self.not_found)
                    self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
                    self.create_widgets()
                    return
                self.current_galia.scanned_q += 1
                self.current_galia.remain_q -= 1
                self.scanned_fx = Scanned()
                self.scanned_fx.id_galia = self.current_galia.id
                self.scanned_fx.reference = self.current_galia.reference
                self.scanned_fx.counter = self.fx_cpt
                if self.current_galia.remain_q == 0:
                    # Close the Galia
                    self.step_num = 0
                    self.scan_config = self.packing_config.get("BOX", None)
                    if not self.scan_config:
                        messagebox.showerror("Error", "Box configuration not found in packaging settings.")
                        exit(1)
                    self.scan_step = "VALIDATION"
                    self.box_barcode_count = len(self.scan_config)
                    if self.box_barcode_count < 3:
                        messagebox.showerror("Error", "Box configuration must have at least 3 Barcodes.")
                        exit(1)
                    self.barcode_specs = self.scan_config[self.step_num]
                    self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
                    self.barcode_prefix = self.barcode_specs["prefix"]
                    self.barcode_img = self.barcode_specs.get("photo", self.not_found)
                    self.fx_cpt = None
                    self.create_widgets()
                    return
                else:
                    self.scanned_fx.save()
                    print(f"FX Scanned: {self.scanned_fx.to_dict()}")
                    self.current_galia.update()
                    print(f"Scanned FX: {self.current_galia.scanned_q} / {self.current_galia.total_q}")
                    self.scan_step = "FX"
                    self.label_step = 0
                    self.fx_label = self.labels_list[self.label_step]
                    self.label_barcodes = self.scan_config[self.fx_label]
                    self.step_num = 0
                    self.barcode_specs = self.label_barcodes[self.step_num]
                    self.barcode_prefix = self.barcode_specs["prefix"]
                    self.barcode_img = self.barcode_specs.get("photo", self.not_found)
                    self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
                    self.fx_cpt = None
                    self.activebox_set(self.current_galia.nr_galia,
                                       self.current_galia.reference,
                                       self.current_galia.total_q,
                                       self.current_galia.scanned_q,
                                       self.current_galia.remain_q)
                    self.create_widgets()
                    return
        elif self.scan_step == "VALIDATION":
            if self.step_num < self.box_barcode_count:
                self.barcode_specs = self.scan_config[self.step_num]
                self.barcode_prefix = self.barcode_specs["prefix"]
                self.barcode_img = self.barcode_specs.get("photo", self.not_found)
                self.scan_msg = self.barcode_specs.get("barcode", "Unknown") + f" {self.scan_step}"
                self.create_widgets()
                return
            # print Box Label Completion
            self.scanned_fx.save()
            print(f"FX Scanned: {self.scanned_fx.to_dict()}")
            self.current_galia.status = "closed"
            self.current_galia.update()
            print(f"Scanned FX: {self.current_galia.nr_galia} is Closed")
            print(f"Scanned Box: {self.current_galia.to_dict()}")
            ####Print the Box Label####
            ###########################
            tsc_label(self.current_galia.nr_galia,
                      self.current_galia.reference,
                      self.current_galia.total_q,
                      self.user_infos["usercard"],
                      datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                      )
            self.init_vars()
            self.activebox_vars()
            self.create_widgets()
        print("Next Step Failed")
        self.init_vars()
        self.activebox_vars()
        self.create_widgets()
        return