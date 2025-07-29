import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from models.engine.app_tools import picking_db_conn
from models.engine.app_tools import get_line_details
from models.engine.db_manager import set_db_conn
from models.engine.db_manager import get_connection
from models.engine.db_manager import get_scanned_harnesses_by_shift
from models.engine.db_manager import get_scanned_fx_per_hour
from models.engine.shift import get_current_shift
from models.engine.shift import working_hours
from models.engine.app_tools import get_line_id
from models.engine.app_tools import get_dashboard_config
from models.engine.app_tools import get_expected_fx
from models.engine.packaging_manager import check_packaging_config
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import math
import os
import json

class ProductionDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Production Dashboard")
        self.geometry("1920x1080")
        self.configure(bg="white")
        # DATABASE
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
        self.production_config = get_dashboard_config()
        print(self.production_config)
        self.scanned_fx = {}
        self.header1_labels = {}
        self.header2_labels = {}
        # Simulated data
        self.load_data()

        # UI Setup
        self.create_header1()
        self.create_header2()
        self.create_charts()
        self.create_efficiency_gauge()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Reload data and refresh dashboard every 3 seconds."""
        self.load_data()
        
        # refresh UI components if they change over time
        self.production_config = get_dashboard_config()
        self.supervisor = self.production_config.get("team_speaker", "Unknown")
        self.ops = self.production_config.get("line_operators", 0)
        self.pops = self.production_config.get("present_operators", 0)
        self.aop = self.ops - self.pops
        prod_infos = [
            ("Supervisor", self.supervisor, "#ff7514"),
            ("Project", self.project, "#ff7514"),
            ("Famille", self.famille, "#ff7514"),
            ("Line", self.line, "#ff7514"),
            ("Shift", self.shift_range, "#ff7514"),
            ("Line Operators", self.ops, "#3F51B5"),
            ("Present OP", self.pops, "#4CAF50"),
            ("Absent OP", self.aop, "#F44336"),
            ("Date/Time", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "#ff7514"),
        ]
        for label, value, _ in prod_infos:
            if label in self.header1_labels:
                self.header1_labels[label].config(text=str(value))
        
        header2_dt = {
            "Shift Target": self.shift_target,
            "Expected": self.expected,
            "Delivered": self.delivered,
            "Gap": self.gap
            }
        for label, value in header2_dt.items():
            if label in self.header2_labels:
                self.header2_labels[label].config(text=str(value))
        # Refresh Charts
        
        # Output per hour
        self.th = self.production_config.get("target_per_hour", 0)
        labels = [t[0] for t in self.output_per_hour]
        values = [t[1] for t in self.output_per_hour]

        self.ax2.clear()
        self.ax2.bar(labels, values, color="orange")
        self.ax2.axhline(y=20, color='green', linestyle='--', label=self.th)
        self.ax2.set_title("Output per Hour")
        self.ax2.set_ylabel("Qty")
        self.ax2.set_xlabel("Hour")
        self.ax2.set_xticklabels(labels, rotation=45, ha='right')
        self.ax2.legend()
        self.canvas2.draw()

        print("🔁 Dashboard refreshed at", datetime.datetime.now())

        # Call this method again after 3000 milliseconds (3 seconds)
        self.after(3000, self.refresh_dashboard)

    def load_data(self):
        self.working_hours = working_hours()
        line_id = get_line_id()
        if not line_id:
            messagebox.showerror("Error", "Line ID not found in settings.")
            return
        print(f"Line ID: {line_id}")
        line_details = get_line_details(line_id)
        (print(line_details))
        if not line_details:
            messagebox.showerror("Error", f"Line {line_id} not found in Database.")
            return
        try:
            self.shift_name, self.shift_range = get_current_shift()
            if self.shift_name:
                print(f"✅ Current time is within {self.shift_name} ({self.shift_range})")
            else:
                print("⚠️ Current time does not match any shift.")
        except Exception as e:
            print(f"❌ Error: {e}")
        self.scanned_fx = get_scanned_harnesses_by_shift(self.shift_range)
        print(f"Scanned FX: {self.scanned_fx}")
        self.supervisor = self.production_config.get("team_speaker", "Unknown")
        self.project = line_details.get("project", "Unknown")
        self.famille = line_details.get("famille", "Unknown")
        self.line = line_details.get("line_id", "Unknown")
        self.ops = self.production_config.get("line_operators", 0)
        self.pops = self.production_config.get("present_operators", 0)
        self.aop = self.ops - self.pops
        self.prod_infos = [
            ("Supervisor", self.supervisor, "#ff7514"),
            ("Project", self.project, "#ff7514"),
            ("Famille", self.famille, "#ff7514"),
            ("Line", self.line, "#ff7514"),
            ("Shift", self.shift_range, "#ff7514"),
            ("Line Operators", self.ops, "#3F51B5"),
            ("Present OP", self.pops, "#4CAF50"),
            ("Absent OP", self.aop, "#F44336"),
            ("Date/Time", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "#ff7514"),
        ]

        self.shift_target = self.production_config.get("shift_target", 0)
        self.expected = get_expected_fx(self.shift_range, self.shift_target)
        self.delivered = len(self.scanned_fx) #harness Scanned Count
        self.gap = self.delivered - self.expected
        self.efficiency_values = [60.62, 53.89, 80.68, 22.01, 26.94, 76.13, 0, 0, 0]
        self.output_per_hour = get_scanned_fx_per_hour(self.shift_range)
        print(self.output_per_hour)
        
        self.info_prod = [
            ("Shift Target", self.shift_target, "#2196F3"),
            ("Expected", self.expected, "#03A9F4"),
            ("Delivered", self.delivered, "#4CAF50"),
            ("Gap", self.gap, "#8BC34A" if self.gap >= 0 else "#FFC107"),
        ]

    def create_header1(self):
        frame = tk.Frame(self, bg="#f8f4f2")
        frame.pack(fill='x', pady=10)

        for label, value, color in self.prod_infos:
            box = tk.Frame(frame, bg=color, bd=2, relief="ridge", padx=25, pady=10)
            box.pack(side='left', padx=8, fill='both', expand=True)
            tk.Label(box, text=label, bg=color, fg="black", font=("Arial", 14, "bold")).pack()
            val_label = tk.Label(box, text=str(value), bg=color, fg="white", font=("Arial", 20, "bold"))
            val_label.pack()
            self.header1_labels[label] = val_label

    def create_header2(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill='x', pady=10)

        
        for label, value, color in self.info_prod:
            box = tk.Frame(frame, bg=color, bd=2, relief="ridge", padx=20, pady=10)
            box.pack(side='left', padx=20, fill='both', expand=True)
            tk.Label(box, text=label, bg=color, fg="white", font=("Arial", 24, "bold")).pack()
            val_label = tk.Label(box, text=str(value), bg=color, fg="white", font=("Arial", 40, "bold"))
            val_label.pack()
            self.header2_labels[label] = val_label
        
    def create_charts(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Efficiency
        fig1 = Figure(figsize=(5, 3), dpi=100)
        self.ax1 = fig1.add_subplot(111)
        self.ax1.plot(self.efficiency_values, marker='o', label='Efficiency')
        self.ax1.axhline(y=100, color='green', linestyle='--', label='Target: 100%')
        self.ax1.set_title("Efficiency per Hour")
        self.ax1.set_ylim([0, 140])
        self.ax1.set_ylabel("Efficiency %")
        self.ax1.set_xlabel("Time slots")
        self.ax1.legend()

        self.canvas1 = FigureCanvasTkAgg(fig1, master=frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(side='left', fill='both', expand=True)

        # Output per hour
        labels = [t[0] for t in self.output_per_hour]
        values = [t[1] for t in self.output_per_hour]
        self.th = self.production_config.get("target_per_hour", 0)

        fig2 = Figure(figsize=(5, 3), dpi=100)
        self.ax2 = fig2.add_subplot(111)

        self.ax2.bar(labels, values, color="orange")
        self.ax2.axhline(y=self.th, color='green', linestyle='--', label=self.th)
        self.ax2.set_title("Output per Hour")
        self.ax2.set_ylabel("Qty")
        self.ax2.set_xlabel("Hour")
        self.ax2.set_xticklabels(labels, rotation=45, ha='right')
        self.ax2.legend()

        self.canvas2 = FigureCanvasTkAgg(fig2, master=frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(side='left', fill='both', expand=True)

    def create_efficiency_gauge(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(pady=20)

        try:
            eff_percent = (self.delivered / self.shift_target) * 100
        except:
            eff_percent = 0.0
        
        canvas = tk.Canvas(frame, width=250, height=150, bg='white', highlightthickness=0)
        canvas.pack()

        # Draw semicircle background
        canvas.create_arc(10, 10, 240, 240, start=130, extent=50, outline='red', style='arc', width=25)
        canvas.create_arc(10, 10, 240, 240, start=95, extent=40, outline='orange', style='arc', width=25)
        canvas.create_arc(10, 10, 240, 240, start=50, extent=40, outline='yellow', style='arc', width=25)
        canvas.create_arc(10, 10, 240, 240, start=0, extent=50, outline='green', style='arc', width=25)

        # Draw needle
        angle = 180 * (eff_percent / 100)
        radians = math.radians(180 - angle)
        x = 125 + 90 * math.cos(radians)
        y = 125 - 90 * math.sin(radians)
        canvas.create_line(125, 125, x, y, fill='green', width=4)

        # Center circle
        canvas.create_oval(120, 120, 130, 130, fill='black')

        canvas.create_text(125, 140, text=f"{eff_percent:.1f}%", font=("Arial", 16, "bold"), fill='black')



if __name__ == "__main__":
    app = ProductionDashboard()
    app.mainloop()
