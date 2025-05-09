import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db


class ViewEditorialFrame(tk.Frame):
    def __init__(self, parent, controller, editorial_id=None):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Visualitzar Editorial", font=("Arial", 18)).pack(pady=20)

        # Datos cargados
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=10)

        # Crear un frame para los botones
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        if editorial_id:
            self.refresh(editorial_id)

    def refresh(self, editorial_id):
        # Destruir y recrear el data_frame
        self.data_frame.destroy()
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=10)

        # Destruir y recrear el button_frame
        self.button_frame.destroy()
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        # Datos cargados
        editorial = self.controller.get_editorial_by_id(editorial_id)

        if editorial:
            editorial_data = [
                editorial["id"], editorial["name"], editorial["address"], editorial["phone"], editorial["email"],
                editorial["website"], editorial["country"], editorial["city"], editorial["postal_code"]
            ]
        else:
            editorial_data = None

        if editorial_data:
            data_labels = [
                "ID", "Nom", "Adreça", "Telèfon", "Correu", "Web", "País", "Ciutat", "Codi Postal"
            ]
            for i, value in enumerate(editorial_data):
                tk.Label(self.data_frame, text=f"{data_labels[i]}: {value}", font=("Arial", 14)).pack(anchor="w")
        else:
            messagebox.showwarning("Atenció", "Editorial no trobada.")
            self.go_back()
            return

        # Crear los botones dentro del button_frame
        tk.Button(self.button_frame, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(side="left", padx=5)

    def go_back(self):
        from classes.editorial.ManageEditorialsFrame import ManageEditorialsFrame
        self.controller.show_frame(ManageEditorialsFrame)
