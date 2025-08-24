import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
from models.job import Job
from models.picking import Picking
from models.engine.picking_manager import update_orders
from models.engine.app_tools import picking_db_conn
from models.engine.app_tools import get_line_id
from models.engine.app_tools import picking_db_conn
from models.engine.app_tools import get_line_details
from models.engine.db_manager import set_db_conn
from models.engine.db_manager import get_connection
from models.engine.db_manager import get_obj
from models.engine.picking_manager import check_fusebox
from models.engine.shift import get_current_shift
from models.engine.job_manager import jobs_by_line
from models.engine.app_tools import insert_harness_track
from models.engine.app_tools import insert_harness_details
from models.engine.printer import tsc_label
from models.engine.printer import godex_label
from models.engine.counter import next_id


class PickingBody(tk.Frame):
    def __init__(self, parent, user_infos, picking_type, counter_length=6):
        self.user_infos = user_infos
        self.picking_type = picking_type
        self.counter_length = counter_length
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        # Initialize variables
        self.jobs = []
        self.opened_batch = None
        self.ref_obj = None
        self.new_batch = False
        self.current_batch = None
        self.nr_batch = None
        self.batch_ref = None
        self.active_ref = "-------"
        self.active_qt = 0
        self.active_picked = 0
        self.active_remain = 0
        self.scan_status = 0
        self.scan_msg = ""
        self.scan_pic = ""
        self.fusebox = None
        self.cpt = ""
        self.picking_barcode = None
        self.active_job = {}
        # load database settings
        db_settings = picking_db_conn()
        if get_connection(db_settings) is None:
            print("Error Connecting to Database")
            messagebox.showerror("Error Connecting to Database.", 
                                 "Please check your database settings in the config file.")
            exit(1)
        else:
            print(db_settings)
            set_db_conn(db_settings)
            self.create_widgets()

    def create_widgets(self):
        # get production lin details
        print(f"Scan Status: {self.scan_status}")
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
        # Picking Process====>
        # ================

        def picking_scan(event):
            input = self.text_entry.get().strip()
            print(f"Scanned Input: {input}")
            if not input or input == "":
                return
            if self.picking_type == "batch":
                if self.scan_status == 0:
                    if self.fusebox is not None:
                        if input != self.fusebox:
                            messagebox.showerror("Error", f"Invalid Fusebox Barcode: {input}")
                            self.text_entry.delete(0, tk.END)
                            return
                    else:
                        if input != "OK":
                            messagebox.showerror("Error", f"Invalid Barcode: {input}")
                            self.text_entry.delete(0, tk.END)
                            return
                    self.text_entry.delete(0, tk.END)
                    self.cpt = next_id(self.counter_length)
                    self.picking_barcode = self.cpt + self.active_job["reference"]
                    print(f"Picking Barcode: {self.picking_barcode}")
                    # print picking label
                    print(f"Picking scan: {input}")
                    godex_label("label_picking",
                                {"ref": self.active_job["reference"],
                                "op": self.user_infos["usercard"],
                                "line_id": line_id,
                                "date_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                "cpt": self.picking_barcode,
                                "l": len(self.picking_barcode)})
                    self.scan_status = 1
                    self.scan_msg = "Confirm picking Label Barcode"
                    self.scan_pic = "./app_images/label.png"
                    self.create_widgets() # Refresh the UI
                elif self.scan_status == 1:
                    if input != self.picking_barcode or self.picking_barcode is None:
                        messagebox.showerror("Error", f"Invalid Picking Barcode: {input}")
                        self.text_entry.delete(0, tk.END)
                        return
                    self.text_entry.delete(0, tk.END)
                    self.active_job["picked"] += 1
                    self.current_batch.scanned_q += 1
                    self.active_job["remain"] -= 1
                    self.current_batch.remain_q -= 1
                    self.active_job["usercard"] = self.user_infos["usercard"]
                    self.current_batch.usercard = self.user_infos["usercard"]
                    if self.active_job["remain"] == 0:
                        self.active_job["job_status"] = "closed"
                        self.current_batch.status = "closed"
                        self.active_job["job_order"] = 0
                        self.current_batch.update()
                        Job(**self.active_job).update()
                        update_orders(line_id)
                    else:
                        self.current_batch.update()
                        Job(**self.active_job).update()
                    print(f"Harness From Ref : {self.active_job['reference']} is Picked")
                    insert_harness_track(self.active_job["reference"],
                                         self.cpt,
                                         line_id,
                                         'Picking',
                                         'OK',
                                         self.active_job["id"],
                                         self.active_job["usercard"])
                    insert_harness_details(self.active_job["reference"],
                                           self.cpt,
                                           line_id,
                                           'Picking',
                                           'OK',
                                           self.active_job["id"],
                                           self.active_job["usercard"])
                    self.scan_status = 0
                    self.create_widgets() # Refresh the UI
                return
            elif self.picking_type == "local":
                if self.scan_status == 0:
                    # scan galia reference
                    self.batch_ref = input[1:]
                    self.ref_obj = get_obj("reference", "ref", self.batch_ref)
                    print(f"Scanned Reference: {self.batch_ref}")
                    print(f"found Reference: {self.ref_obj}")
                    if not self.ref_obj:
                        messagebox.showerror("Error", f"Reference {self.batch_ref} not found in database.")
                        self.text_entry.delete(0, tk.END)
                        self.init_vars()
                        self.create_widgets() # Refresh the UI
                        return
                    self.opened_batch = get_obj("picking", "reference", self.batch_ref)
                    self.active_ref = self.ref_obj.get("ref", "N/A")
                    self.fusebox = check_fusebox(self.active_ref)
                    self.scan_msg = "Scan Nr Galia Barcode"
                    self.scan_pic = "./app_images/picking/galia_nr.jpg"
                    self.scan_status = 1
                    self.text_entry.delete(0, tk.END)
                    self.create_widgets() # Refresh the UI
                    return
                elif self.scan_status == 1:
                    # Scan Nr Galia barcode
                    self.nr_batch = input[1:]
                    if self.opened_batch and self.opened_batch.get("status", "N/A") == "open":
                        if self.opened_batch.get("batch_id", "N/A") != self.nr_batch:
                            messagebox.showerror("Error", f"Reference {self.active_ref} is already opened for another Batch_id.")
                            self.text_entry.delete(0, tk.END)
                            self.init_vars()
                            self.create_widgets()
                            return
                    else:
                        self.opened_batch = get_obj("picking", "batch_id", self.nr_batch)
                        if not self.opened_batch:
                            self.new_batch = True
                            self.current_batch = Picking()
                            self.current_batch.batch_id = self.nr_batch
                            self.current_batch.reference = self.active_ref
                            self.current_batch.line_id = line_id
                            self.current_batch.status = "open"
                            self.current_batch.total_q = 0
                            self.current_batch.scanned_q = 0
                            self.current_batch.remain_q = 0
                            #self.current_batch.usercard = self.user_infos["usercard"]
                            self.scan_msg = "Scan Galia Quantity Barcode"
                            self.scan_pic = "./app_images/picking/galia_q.jpg"
                            self.text_entry.delete(0, tk.END)
                            self.scan_status = 2
                            self.create_widgets() # Refresh the UI
                            return
                        elif self.opened_batch.get("status", "N/A") == "closed":
                            messagebox.showerror("Error", f"Galia {self.nr_batch} is already closed.")
                            self.text_entry.delete(0, tk.END)
                            self.init_vars()
                            self.create_widgets() # Refresh the UI
                            return
                        elif self.opened_batch.get("reference", "N/A") != self.active_ref:
                            messagebox.showerror("Error", f"Galia {self.nr_batch} reference mismatch.")
                            self.text_entry.delete(0, tk.END)
                            self.init_vars()
                            self.create_widgets()
                            return
                    self.current_batch = Picking(**self.opened_batch)
                    self.active_qt = self.current_batch.total_q
                    self.active_picked = self.current_batch.scanned_q
                    self.active_remain = self.current_batch.remain_q
                    self.scan_msg = "Scan Galia Quantity Barcode"
                    self.scan_pic = "./app_images/picking/galia_q.jpg"
                    self.text_entry.delete(0, tk.END)
                    self.scan_status = 2
                    self.create_widgets() # Refresh the UI
                    return
                elif self.scan_status == 2:
                    try:
                        quantity = int(input[1:])
                        if quantity <= 0:
                            raise ValueError("Quantity must be positive.")
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid Quantity: {input}")
                        self.text_entry.delete(0, tk.END)
                        self.init_vars()
                        self.create_widgets()
                        return
                    if self.new_batch is False:
                        if self.current_batch.total_q != quantity:
                            messagebox.showerror("Error", f"Quantity mismatch for Galia {self.nr_batch}. Expected {self.current_batch.total_q}, got {quantity}.")
                            self.text_entry.delete(0, tk.END)
                            self.init_vars()
                            self.create_widgets()
                            return
                    else:
                        self.current_batch.total_q = quantity
                        self.current_batch.usercard = self.user_infos["usercard"]
                        self.current_batch.save()
                    self.active_qt = self.current_batch.total_q
                    self.text_entry.delete(0, tk.END)
                    self.fusebox_vars()
                    self.scan_status = 3
                    self.create_widgets()
                    return   
                elif self.scan_status == 3:
                    if self.fusebox:
                        if input != self.ref_obj.get("fuse_box", "N/A"):
                            messagebox.showerror("Error", f"Invalid Fusebox Barcode: {input}")
                            self.text_entry.delete(0, tk.END)
                            self.init_vars()
                            self.create_widgets()
                            return
                    else:
                        if input != "OK":
                            messagebox.showerror("Error", f"Invalid OK Barcode: {input}")
                            self.text_entry.delete(0, tk.END)
                            self.init_vars()
                            self.create_widgets()
                            return
                    self.cpt = next_id(self.counter_length)
                    print(f"New Harness Counter: {self.cpt}")
                    self.scan_status = 4
                    self.scan_msg = "Confirm Picking Label"
                    self.scan_pic = "./app_images/picking/label.png"    
                    self.current_batch.usercard = self.user_infos["usercard"]
                    print(f"Galia Nr: {self.current_batch.batch_id} for Ref: {self.current_batch.reference} with Quantity: {self.current_batch.total_q} is Created")
                    self.scan_msg = "Confirm Picking Label"
                    self.scan_pic = "./app_images/picking/picking_label.png"
                    # print galia label
                    godex_label("label_picking",
                                {"ref": self.current_batch.reference,
                                "op": self.user_infos["usercard"],
                                "line_id": line_id,
                                "date_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                "cpt": self.current_batch.batch_id})
                    self.text_entry.delete(0, tk.END)
                    self.create_widgets()
                    return
                elif self.scan_status == 4:
                    if input[1:] != self.current_batch.reference:
                        messagebox.showerror("Error", f"Invalid Pickng Label Barcode: {input}")
                        self.text_entry.delete(0, tk.END)
                        self.init_vars()
                        self.create_widgets()
                        return
                    self.current_batch.scanned_q += 1
                    self.current_batch.remain_q = self.current_batch.total_q - self.current_batch.scanned_q
                    self.active_picked = self.current_batch.scanned_q
                    self.active_remain = self.current_batch.remain_q
                    self.current_batch.usercard = self.user_infos["usercard"]
                    print(f"Harness From Galia Nr : {self.current_batch.batch_id} is Picked")
                    insert_harness_track(self.current_batch.reference,
                                         self.cpt,
                                         line_id,
                                         'Picking',
                                         'OK',
                                         self.current_batch.batch_id,
                                         self.current_batch.usercard)
                    insert_harness_details(self.current_batch.reference,
                                           self.cpt,
                                           line_id,
                                           'Picking',
                                           'OK',
                                           self.current_batch.batch_id,
                                           self.current_batch.usercard)
                    if self.current_batch.remain_q == 0:
                        self.current_batch.status = "closed"
                        self.current_batch.update()
                        self.text_entry.delete(0, tk.END)
                        self.init_vars()
                        self.create_widgets()
                        return
                    self.current_batch.update()
                    self.fusebox_vars()
                    self.scan_status = 3
                    self.create_widgets()
                    return
        # Configure row weights: 3/4 for top content, 1/4 for table
        self.rowconfigure(0, weight=0)  # Prod Bar
        self.rowconfigure(1, weight=0)  # Active Reference
        self.rowconfigure(2, weight=3)  # Picking frame
        self.rowconfigure(3, weight=1)  # Table
        self.columnconfigure(0, weight=1)

        # ======================
        # Production Line informations
        # ======================
        self.prodbar = tk.Frame(self, bg="#909192", height=100)
        self.prodbar.columnconfigure(0, weight=1)
        self.prodbar.grid(row=0, column=0, sticky="ew")
        # Create labels for project, family, line, and shift
        # ======================
        project_label = tk.Label(self.prodbar, text=f"Project : {project}", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        project_label.pack(side="left", padx=(0, 0), fill="both", expand=True)
        separator = tk.Label(self.prodbar, text="•", font=("Arial", 18, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        famille_label = tk.Label(self.prodbar, text=f"Famille : {famille}", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        famille_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.prodbar, text="•", font=("Arial", 18, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        line_label = tk.Label(self.prodbar, text=f"Line : {line}", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        line_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        separator = tk.Label(self.prodbar, text="•", font=("Arial", 18, "bold"),
                             bg="#909192", fg="black")
        separator.pack(side="left", padx=10, fill="both", expand=True)
        shift_label = tk.Label(self.prodbar, text=f"Shift : {shift_range}", font=("Arial", 18, "bold"),
                         bg="#909192", fg="white")
        shift_label.pack(side="left", padx=(10, 0), fill="both", expand=True)
        ##======Picking Type=====##
        if self.picking_type == "batch":
            self.jobs = jobs_by_line(line)
            for job in self.jobs:
                if job.get("job_order") == 1:
                    self.active_job = job
                    self.current_hns = get_obj("picking", "batch_id", job.get("id", ""))
                    if not self.current_hns:
                        self.current_hns = {}
                        self.current_hns["batch_id"] = job["id"]
                        self.current_hns["reference"] = job["reference"]
                        self.current_hns["line_id"] = job["line_id"]
                        self.current_hns["status"] = "open"
                        self.current_hns["total_q"] = job["quantity"]
                        self.current_hns["scanned_q"] = job["picked"]
                        self.current_hns["remain_q"] = job["remain"]
                        self.current_hns["usercard"] = self.user_infos["usercard"]
                        self.current_batch = Picking(**self.current_hns)
                        self.current_batch.save()
                    else:
                        self.current_batch = Picking(**self.current_hns)
                    break
            self.active_ref = self.active_job.get("reference", "N/A")
            self.active_qt = self.active_job.get("quantity", 0)
            self.active_picked = self.active_job.get("picked", 0)
            self.active_remain = self.active_job.get("remain", 0)
            ### check if fusebox is required
            self.fusebox = check_fusebox(self.active_ref)
            if self.fusebox and self.scan_status == 0:
                self.scan_msg = "Scan FuseBox Barcode"
                self.scan_pic = "./app_images/picking/fusebox.jpeg"
            elif self.scan_status == 0:
                self.scan_msg = "Scan OK Barcode"
                self.scan_pic = "./app_images/picking/ok.webp"    
        else:
            if self.scan_status == 0:
                self.scan_msg = "Scan Reference Galia Barcode"
                self.scan_pic = "./app_images/picking/galia_ref.jpg"
                self.active_ref = "-------"
                self.active_qt = 0
                self.active_picked = 0
                self.active_remain = 0
        # ======================
        # Active Picking Reference
        # ======================
        self.activeref_frame = tk.Frame(self, bg="#0CC506", height=50)
        self.activeref_frame.grid(row=1, column=0, sticky="ew")
        self.activeref_frame.columnconfigure(0, weight=1)
        ref_label = tk.Label(self.activeref_frame, text=f"Reference : {self.active_ref}", font=("Arial", 18, "bold"),
                        bg="#0CC506", fg="#0D0D0E")
        ref_label.pack(side="left", padx=(10, 0))
        separator = tk.Label(self.activeref_frame, text="•••", font=("Arial", 18, "bold"),
                            bg="#0CC506", fg="white")
        separator.pack(side="left", padx=10)
        qt_label = tk.Label(self.activeref_frame, text=f"Quantite Total : {self.active_qt}", font=("Arial", 18, "bold"),
                        bg="#0CC506", fg="#0D0D0E")
        qt_label.pack(side="left", padx=(10, 0))
        separator = tk.Label(self.activeref_frame, text="•••", font=("Arial", 18, "bold"),
                            bg="#0CC506", fg="white")
        separator.pack(side="left", padx=10)
        p_label = tk.Label(self.activeref_frame, text=f"Picked : {self.active_picked}", font=("Arial", 18, "bold"),
                        bg="#0CC506", fg="#0D0D0E")
        p_label.pack(side="left", padx=(10, 0))
        separator = tk.Label(self.activeref_frame, text="•••", font=("Arial", 18, "bold"),
                            bg="#0CC506", fg="white")
        separator.pack(side="left", padx=10)
        r_label = tk.Label(self.activeref_frame, text=f"Reste : {self.active_remain}", font=("Arial", 18, "bold"),
                        bg="#0CC506", fg="#0D0D0E")
        r_label.pack(side="left", padx=(10, 0))
        # ======================
        # Top Frame (Image + Entry)
        # ======================
        self.top_frame = tk.Frame(self, bg="white")
        self.top_frame.grid(row=2, column=0, sticky="nsew")
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.rowconfigure((0, 1), weight=1)
        self.message_label = tk.Label(
            self.top_frame,
            text=self.scan_msg,
            font=("Arial", 30, "bold"),
            justify="center",
            bg="white",
            fg="#0515F8"
        )
            # Image
        try:
            img = Image.open(self.scan_pic)
            img = img.resize((800, 400), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            image_label = tk.Label(self.top_frame, image=self.photo, bg="white", borderwidth=1, relief="solid")
            image_label.grid(row=1, column=0, pady=(20, 10))
        except Exception as e:
            image_label = tk.Label(self.top_frame, text="Image not found", bg="white")
            image_label.grid(row=1, column=0)
        self.message_label.grid(row=0, column=0, pady=(10, 0))

    

        # Entry Field
        self.text_entry = tk.Entry(self.top_frame, font=("Arial", 16), justify="center", bg="#e0e0e0", relief="solid")
        self.text_entry.grid(row=2, column=0, ipadx=50, ipady=5, pady=(0, 20))
        self.text_entry.focus_set()
        self.text_entry.bind("<Return>", picking_scan)
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
            columns=("reference", "line", "quantity", "picked", "remain", "status", "order"),
            show="headings",
            height=5
        )
        self.tree.heading("reference", text="Reference")
        self.tree.heading("line", text="Line ID")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("picked", text="Picked")
        self.tree.heading("remain", text="Remaining")
        self.tree.heading("status", text="Status")
        self.tree.heading("order", text="Order")
        self.tree.column("reference", width=80)
        self.tree.column("line", width=40)
        self.tree.column("quantity", width=40)
        self.tree.column("picked", width=40)
        self.tree.column("remain", width=40)
        self.tree.column("status", width=80)
        self.tree.column("order", width=40)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(footer, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Sample Data
        
        for job in self.jobs:
            print(f"Job: {job}")
            if job.get("job_order") == 1:
                continue
            else:
                # Assuming job is a dictionary with the required keys
                self.tree.insert("", "end", values=(
                    job.get("reference", "N/A"),
                    job.get("line_id", "N/A"),
                    job.get("quantity", 0),
                    job.get("picked", 0),
                    job.get("remain", 0),
                    job.get("job_status", "N/A"),
                    job.get("job_order", "N/A")
                ))

    def init_vars(self):
        self.jobs = []
        self.opened_batch = None
        self.ref_obj = None
        self.new_batch = False
        self.current_batch = None
        self.nr_batch = None
        self.batch_ref = None
        self.active_ref = "-------"
        self.active_qt = 0
        self.active_picked = 0
        self.active_remain = 0
        self.scan_status = 0
        self.scan_msg = ""
        self.scan_pic = ""
        self.fusebox = None
        self.cpt = ""
        self.picking_barcode = None
        self.active_job = {}
        self.current_hns = {}
        return

    def fusebox_vars(self):
        if self.fusebox:
            self.scan_msg = "Scan FuseBox Barcode"
            self.scan_pic = "./app_images/picking/fusebox.jpeg"
            return
        self.scan_msg = "Scan OK Barcode"
        self.scan_pic = "./app_images/picking/ok.webp"
        return
