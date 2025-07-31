import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login Page")
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

        welcome_label = tk.Label(self.left_frame, text="WELCOME", font=("Helvetica", 32, "bold"), fg="white", bg="#0f0f0f")
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

        profile_icon = tk.Canvas(self.right_frame, width=100, height=100, bg="#0f0f0f", highlightthickness=0)
        profile_icon.create_oval(10, 10, 90, 90, fill="#1e90ff")
        profile_icon.pack(pady=(80, 10))

        signin_label = tk.Label(self.right_frame, text="Sign In", font=("Helvetica", 20, "bold"), fg="white", bg="#0f0f0f")
        signin_label.pack(pady=(0, 20))

        # Username
        self.create_input_field("Username", "\U0001F464")
        # Password
        self.create_input_field("Password", "\U0001F512", show="*")

        # Login Button
        login_btn = tk.Button(self.right_frame, text="LOGIN", font=("Helvetica", 14, "bold"), bg="#1e90ff", fg="white",
                              width=20, height=2, bd=0, relief="flat", cursor="hand2",
                              activebackground="#1c86ee", command=self.login)
        login_btn.pack(pady=(20, 10))

        forgot_label = tk.Label(self.right_frame, text="Forgot Password ?", font=("Helvetica", 10), fg="#5dade2", bg="#0f0f0f", cursor="hand2")
        forgot_label.pack(pady=(0, 40))

        # Signup
        signup_frame = tk.Frame(self.right_frame, bg="#0f0f0f")
        signup_frame.pack()
        no_account = tk.Label(signup_frame, text="No account yet? ", font=("Helvetica", 10), fg="white", bg="#0f0f0f")
        no_account.pack(side="left")
        signup_now = tk.Label(signup_frame, text="SIGN UP NOW", font=("Helvetica", 10, "bold"), fg="#00bfff", bg="#0f0f0f", cursor="hand2")
        signup_now.pack(side="left")

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

        if label_text == "Username":
            self.username_entry = entry
        elif label_text == "Password":
            self.password_entry = entry

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "admin" and password == "admin":
            messagebox.showinfo("Login", "Login successful")
        else:
            messagebox.showerror("Login", "Invalid credentials")

if __name__ == '__main__':
    app = LoginApp()
    app.mainloop()
