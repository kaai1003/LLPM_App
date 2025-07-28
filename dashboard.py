import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import math

class ProductionDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Production Dashboard")
        self.geometry("1920x1080")
        self.configure(bg="white")

        # Simulated data
        self.load_data()

        # UI Setup
        self.create_header1()
        self.create_header2()
        self.create_charts()
        self.create_efficiency_gauge()

    def load_data(self):
        self.prod_infos = [
            ("Team Speaker", "Hicham", "#ff7514"),
            ("Project", "P2JO", "#ff7514"),
            ("Famille", "PPL", "#ff7514"),
            ("Line", "L212", "#ff7514"),
            ("Shift", "22h00-06h00", "#ff7514"),
            ("Line Operators", 60, "#3F51B5"),
            ("Present OP", 53, "#4CAF50"),
            ("Absent OP", 7, "#F44336"),
            ("Date/Time", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "#ff7514"),
        ]

        self.shift_target = 120
        self.expected = 75
        self.delivered = 65
        self.gap = self.delivered - self.expected
        self.efficiency_values = [60.62, 53.89, 80.68, 22.01, 26.94, 76.13, 0, 0, 0]
        self.output_per_hour = [15, 8, 12, 10, 4, 6, 0, 0, 0]
        self.part_data = [("8109443 02", 36), ("8109452 02", 29)]

    def create_header1(self):
        frame = tk.Frame(self, bg="#f8f4f2")
        frame.pack(fill='x', pady=10)

        for label, value, color in self.prod_infos:
            box = tk.Frame(frame, bg=color, bd=2, relief="ridge", padx=25, pady=10)
            box.pack(side='left', padx=8, fill='both', expand=True)
            tk.Label(box, text=label, bg=color, fg="black", font=("Arial", 14, "bold")).pack()
            tk.Label(box, text=str(value), bg=color, fg="white", font=("Arial", 20, "bold")).pack()

    def create_header2(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill='x', pady=10)

        info = [
            ("Shift Target", self.shift_target, "#2196F3"),
            ("Expected", self.expected, "#03A9F4"),
            ("Delivered", self.delivered, "#4CAF50"),
            ("Gap", self.gap, "#8BC34A" if self.gap >= 0 else "#FFC107"),
        ]

        for label, value, color in info:
            box = tk.Frame(frame, bg=color, bd=2, relief="ridge", padx=20, pady=10)
            box.pack(side='left', padx=20, fill='both', expand=True)
            tk.Label(box, text=label, bg=color, fg="white", font=("Arial", 24, "bold")).pack()
            tk.Label(box, text=str(value), bg=color, fg="white", font=("Arial", 40, "bold")).pack()

    def create_charts(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Efficiency
        fig1 = Figure(figsize=(5, 3), dpi=100)
        ax1 = fig1.add_subplot(111)
        ax1.plot(self.efficiency_values, marker='o', label='Efficiency')
        ax1.axhline(y=100, color='green', linestyle='--', label='Target: 100%')
        ax1.set_title("Efficiency per Hour")
        ax1.set_ylim([0, 140])
        ax1.set_ylabel("Efficiency %")
        ax1.set_xlabel("Time slots")
        ax1.legend()

        canvas1 = FigureCanvasTkAgg(fig1, master=frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side='left', fill='both', expand=True)

        # Output per hour
        fig2 = Figure(figsize=(5, 3), dpi=100)
        ax2 = fig2.add_subplot(111)
        ax2.bar(range(len(self.output_per_hour)), self.output_per_hour, color="orange")
        ax2.axhline(y=20, color='green', linestyle='--', label='Target: 15')
        ax2.set_title("Output per Hour")
        ax2.set_ylabel("Qty")
        ax2.set_xlabel("Time slots")
        ax2.legend()

        canvas2 = FigureCanvasTkAgg(fig2, master=frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side='left', fill='both', expand=True)

    def create_efficiency_gauge(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(pady=20)

        eff_percent = (self.delivered / self.shift_target) * 100
        canvas = tk.Canvas(frame, width=250, height=150, bg='white', highlightthickness=0)
        canvas.pack()

        # Draw semicircle background
        canvas.create_arc(10, 10, 240, 240, start=120, extent=50, outline='red', style='arc', width=25)
        canvas.create_arc(10, 10, 240, 240, start=80, extent=50, outline='orange', style='arc', width=25)
        canvas.create_arc(10, 10, 240, 240, start=40, extent=50, outline='yellow', style='arc', width=25)
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
