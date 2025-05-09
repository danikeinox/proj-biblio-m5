import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db


class EditEditorialFrame(tk.Frame):
    def __init__(self, parent, controller, editorial_id=None):
        super().__init__(parent)
        self.controller = controller
        self.editorial_id = editorial_id

        tk.Label(self, text="Editar Editorial", font=("Arial", 18)).pack(pady=20)

        # Datos cargados
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=10)

        self.refresh(editorial_id)

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

    def refresh(self, editorial_id):
        # Destruir y recrear el data_frame
        self.data_frame.destroy()
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=10)

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
            # Entradas de edición
            for i, label in enumerate(data_labels):
                if label == "ID":
                    tk.Label(self.data_frame, text=label, font=("Arial", 14)).grid(row=i, column=0, padx=10, pady=5)
                    entry = tk.Label(self.data_frame, text=editorial_data[i], font=("Arial", 14))
                    entry.grid(row=i, column=1, padx=10, pady=5)
                else:
                    tk.Label(self.data_frame, text=label, font=("Arial", 14)).grid(row=i, column=0, padx=10, pady=5)
                    entry = tk.Entry(self.data_frame, font=("Arial", 14))
                    entry.grid(row=i, column=1, padx=10, pady=5)
                    entry.insert(0, editorial_data[i])

                self.editorial_id = editorial_data[0]
        else:
            messagebox.showwarning("Atenció", "Editorial no trobada.")
            self.go_back()
            return

        # Crear un frame para los botones y colocarlo debajo del data_frame
        if hasattr(self, "button_frame"):
            self.button_frame.destroy()  # Destruir el frame de botones si ya existe

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        tk.Button(self.button_frame, text="Guardar", command=self.update_editorial, font=("Arial", 14)).pack(
            side="left", padx=5)
        tk.Button(self.button_frame, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(side="left", padx=5)

    def update_editorial(self):
        editorial_id = self.data_frame.grid_slaves(row=0, column=1)[0].get()
        name = self.data_frame.grid_slaves(row=1, column=1)[0].get()
        address = self.data_frame.grid_slaves(row=2, column=1)[0].get()
        phone = self.data_frame.grid_slaves(row=3, column=1)[0].get()
        email = self.data_frame.grid_slaves(row=4, column=1)[0].get()
        website = self.data_frame.grid_slaves(row=5, column=1)[0].get()
        country = self.data_frame.grid_slaves(row=6, column=1)[0].get()
        city = self.data_frame.grid_slaves(row=7, column=1)[0].get()
        postal_code = self.data_frame.grid_slaves(row=8, column=1)[0].get()

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE editorial SET name = %s, address = %s, phone = %s, email = %s, website = %s, country = %s, city = %s, postal_code = %s WHERE id = %s",
            (name, address, phone, email, website, country, city, postal_code, editorial_id)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Info", "Editorial actualitzada correctament.")
        self.go_back()

    def go_back(self):
        from classes.editorial.ManageEditorialsFrame import ManageEditorialsFrame
        self.controller.show_frame(ManageEditorialsFrame)
