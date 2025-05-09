import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db


class AddEditorialFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Afegir Editorial", font=("Arial", 18)).pack(pady=20)

        # Nom
        row1 = tk.Frame(self)
        row1.pack(fill="x", pady=5)
        tk.Label(row1, text="Nom:", font=("Arial", 14)).pack(side="left", padx=10)
        self.name_entry = tk.Entry(row1, font=("Arial", 14))
        self.name_entry.pack(side="left", expand=True, fill="x")

        # Adreça
        row2 = tk.Frame(self)
        row2.pack(fill="x", pady=5)
        tk.Label(row2, text="Adreça:", font=("Arial", 14)).pack(side="left", padx=10)
        self.address_entry = tk.Entry(row2, font=("Arial", 14))
        self.address_entry.pack(side="left", expand=True, fill="x")

        # Telèfon
        row3 = tk.Frame(self)
        row3.pack(fill="x", pady=5)
        tk.Label(row3, text="Telèfon:", font=("Arial", 14)).pack(side="left", padx=10)
        self.phone_entry = tk.Entry(row3, font=("Arial", 14))
        self.phone_entry.pack(side="left", expand=True, fill="x")

        # Correu
        row4 = tk.Frame(self)
        row4.pack(fill="x", pady=5)
        tk.Label(row4, text="Correu:", font=("Arial", 14)).pack(side="left", padx=10)
        self.email_entry = tk.Entry(row4, font=("Arial", 14))
        self.email_entry.pack(side="left", expand=True, fill="x")

        # Web
        row5 = tk.Frame(self)
        row5.pack(fill="x", pady=5)
        tk.Label(row5, text="Web:", font=("Arial", 14)).pack(side="left", padx=10)
        self.website_entry = tk.Entry(row5, font=("Arial", 14))
        self.website_entry.pack(side="left", expand=True, fill="x")

        # País
        row6 = tk.Frame(self)
        row6.pack(fill="x", pady=5)
        tk.Label(row6, text="País:", font=("Arial", 14)).pack(side="left", padx=10)
        self.country_entry = tk.Entry(row6, font=("Arial", 14))
        self.country_entry.pack(side="left", expand=True, fill="x")

        # Ciutat
        row7 = tk.Frame(self)
        row7.pack(fill="x", pady=5)
        tk.Label(row7, text="Ciutat:", font=("Arial", 14)).pack(side="left", padx=10)
        self.city_entry = tk.Entry(row7, font=("Arial", 14))
        self.city_entry.pack(side="left", expand=True, fill="x")

        # Codi Postal
        row8 = tk.Frame(self)
        row8.pack(fill="x", pady=5)
        tk.Label(row8, text="Codi Postal:", font=("Arial", 14)).pack(side="left", padx=10)
        self.postal_code_entry = tk.Entry(row8, font=("Arial", 14))
        self.postal_code_entry.pack(side="left", expand=True, fill="x")

        # Botones
        tk.Button(self, text="Registrar", command=self.create_editorial, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

        self.refresh()

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

    def refresh(self):
        # Limpiar los campos de entrada
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.website_entry.delete(0, tk.END)
        self.country_entry.delete(0, tk.END)
        self.city_entry.delete(0, tk.END)
        self.postal_code_entry.delete(0, tk.END)
        self.name_entry.focus_set()

    def create_editorial(self):
        name = self.name_entry.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        website = self.website_entry.get()
        country = self.country_entry.get()
        city = self.city_entry.get()
        postal_code = self.postal_code_entry.get()

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO editorial (name, address, phone, email, website, country, city, postal_code) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (name, address, phone, email, website, country, city, postal_code)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Info", "Editorial afegida correctament.")
        self.go_back()

    def go_back(self):
        from classes.editorial.ManageEditorialsFrame import ManageEditorialsFrame
        self.controller.show_frame(ManageEditorialsFrame)
