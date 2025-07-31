import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from models.engine.db_manager import get_all
from models.engine.app_tools import picking_db_conn
from models.engine.db_manager import set_db_conn
from models.engine.db_manager import get_connection
import os

class LoginApp(tk.Tk):
    def __init__(self, login_success_callback):
        super().__init__()
        self.login_success_callback = login_success_callback
        db_settings = picking_db_conn()
        if get_connection(db_settings) is None:
            print("Error Connecting to Database")
            messagebox.showerror("Error Connecting to Database.", 
                                 "Please check your database settings in the config file.")
            exit(1)
        print(db_settings)
        set_db_conn(db_settings)
        self.title("User Login Interface")
        self.geometry("1200x700")
        self.configure(bg="#f37208")
        self.resizable(False, False)
        self.minsize(1000, 600)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="a")
        self.grid_columnconfigure(1, weight=1, uniform="a")

        self.create_left_frame()
        self.create_right_frame()

    def create_left_frame(self):
        self.left_frame = tk.Frame(self, bg="#f37208")
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        welcome_label = tk.Label(self.left_frame, text="Packaging App", font=("Helvetica", 32, "bold"), fg="white", bg="#f37208")
        welcome_label.pack(pady=(100, 30))

        # Image
        image_path = "./app_images/pack.jpg"  # Update if image is elsewhere
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            image_label = tk.Label(self.left_frame, image=self.photo, bg="#0f0f0f")
            image_label.pack()

    def create_right_frame(self):
        self.right_frame = tk.Frame(self, bg="#f37208")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=40)

        # Load the image (ensure path is correct and image is not too large)
        icon_path = "./icons/login.png"  # Replace with your icon file path
        image = Image.open(icon_path).resize((80, 80))  # Resize if needed
        icon_img = ImageTk.PhotoImage(image)

        # Create canvas and add image
        profile_icon = tk.Canvas(self.right_frame, width=100, height=100, bg="#f37208", highlightthickness=0)
        profile_icon.create_oval(10, 10, 90, 90, fill="#1e90ff")  # Optional background circle
        profile_icon.create_image(50, 50, image=icon_img)  # Center the icon (x=50, y=50)
        profile_icon.pack(pady=(80, 10))

        # Keep a reference to avoid garbage collection
        profile_icon.image = icon_img

        signin_label = tk.Label(self.right_frame, text="User Login", font=("Helvetica", 20, "bold"), fg="white", bg="#f37208")
        signin_label.pack(pady=(0, 20))

        # Username
        self.create_input_field("Usercard", "\U0001F464")
        # Password
        self.create_input_field("Password", "\U0001F512", show="*")

        # Login Button
        login_btn = tk.Button(self.right_frame, text="LOGIN", font=("Helvetica", 14, "bold"), bg="#1e90ff", fg="white",
                              width=20, height=2, bd=0, relief="flat", cursor="hand2",
                              activebackground="#1c86ee", command=self.login)
        login_btn.pack(pady=(20, 10))


    def create_input_field(self, label_text, icon_text, show=None):
        container = tk.Frame(self.right_frame, bg="#f37208")
        container.pack(pady=10, fill="x")

        label = tk.Label(container, text=label_text, font=("Helvetica", 12), fg="white", bg="#0f0f0f")
        label.pack(anchor="w")

        field_frame = tk.Frame(container, bg="white", bd=1)
        field_frame.pack(fill="x")

        icon_label = tk.Label(field_frame, text=icon_text, font=("Helvetica", 12), bg="white")
        icon_label.pack(side="left", padx=5)

        entry = tk.Entry(field_frame, font=("Helvetica", 12), bd=0, relief="flat", show=show, bg="white")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        if label_text == "Usercard":
            self.username_entry = entry
        elif label_text == "Password":
            self.password_entry = entry

    def login(self):
        """Handle login logic"""
        self.all_users = get_all("users")
        if not self.all_users:
            messagebox.showerror("Login", "No users found in the database")
            return
        usercard = self.username_entry.get()
        password = self.password_entry.get()
        for user in self.all_users:
            if user['usercard'] == usercard and user['password'] == password:
                self.destroy()  # Close login window
                self.login_success_callback(user)  # Launch the main app
                return
        messagebox.showerror("Login", "Invalid credentials")
        return

if __name__ == '__main__':
    app = LoginApp()
    app.mainloop()
