import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db


class ManageEditorialsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Gestionar Editorials", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Editorials (selecciona una editorial a gestionar)", font=("Arial", 14)).pack()

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Configuración del Treeview
        self.tree = ttk.Treeview(
            container,
            columns=("id", "name", "address", "phone", "email", "website", "country", "city", "postal_code"),
            show="headings",
        )
        self.tree.pack(side="left", fill="both", expand=True)

        # Encabezados de las columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nom")
        self.tree.heading("address", text="Adreça")
        self.tree.heading("phone", text="Telèfon")
        self.tree.heading("email", text="Correu")
        self.tree.heading("website", text="Web")
        self.tree.heading("country", text="País")
        self.tree.heading("city", text="Ciutat")
        self.tree.heading("postal_code", text="Codi Postal")

        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("address", width=200)
        self.tree.column("phone", width=100)
        self.tree.column("email", width=200)
        self.tree.column("website", width=150)
        self.tree.column("country", width=100)
        self.tree.column("city", width=100)
        self.tree.column("postal_code", width=100)

        # Scrollbar para el Treeview
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Cargar datos
        self.refresh_editorial_data()

        # Eventos
        self.tree.bind("<Double-1>", self.editorial_selected)
        self.tree.bind("<Return>", self.editorial_selected)
        self.tree.bind("<space>", self.editorial_selected)
        self.tree.bind("<Delete>", lambda e: self.delete_editorial())
        self.tree.bind("<Escape>", lambda e: self.controller.show_frame(ManageEditorialsFrame))

        # Botones de acción
        tk.Button(self, text="Visualitzar Editorial", command=self.editorial_selected, font=("Arial", 14)).pack(pady=10,
                                                                                                                padx=10,
                                                                                                                anchor="w",
                                                                                                                side="left")
        tk.Button(self, text="Afegir Editorial", command=self.add_editorial, font=("Arial", 14)).pack(pady=10, padx=10,
                                                                                                      anchor="w",
                                                                                                      side="left")
        tk.Button(self, text="Editar Editorial", command=self.edit_editorial, font=("Arial", 14)).pack(pady=10, padx=10,
                                                                                                       anchor="w",
                                                                                                       side="left")
        tk.Button(self, text="Eliminar Editorial", command=self.delete_editorial, font=("Arial", 14)).pack(pady=10,
                                                                                                           padx=10,
                                                                                                           anchor="w",
                                                                                                           side="left")
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10, padx=10, anchor="w",
                                                                                      side="left")

    def refresh_editorial_data(self):
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Conectar a la base de datos y cargar datos
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM editorial")
        editorials = cursor.fetchall()
        conn.close()

        # Insertar datos en el Treeview
        for editorial in editorials:
            self.tree.insert("", "end", values=editorial)

        self.tree.focus_set()
        self.tree.selection_set(self.tree.get_children()[0])
        self.tree.focus(self.tree.get_children()[0])
        self.tree.see(self.tree.get_children()[0])

    def editorial_selected(self, event=None):
        # Obtener el elemento seleccionado
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item)["values"]
            editorial_id = item_data[0]
            # Llamar al frame de visualización
            from classes.editorial import ViewEditorialFrame
            self.controller.show_frame(ViewEditorialFrame, editorial_id)

    def add_editorial(self):
        # Navegar al frame para añadir editorial
        from classes.editorial import AddEditorialFrame
        self.controller.show_frame(AddEditorialFrame)

    def edit_editorial(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item)["values"]
            editorial_id = item_data[0]
            # Navegar al frame para editar editorial
            from classes.editorial import EditEditorialFrame
            self.controller.show_frame(EditEditorialFrame, editorial_id)
        else:
            messagebox.showwarning("Atenció", "Selecciona una editorial per editar.")

    def delete_editorial(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item)["values"]
            editorial_id = item_data[0]
            # Confirmación de eliminación
            confirm = messagebox.askyesno("Eliminar Editorial", "Estàs segur que vols eliminar aquesta editorial?")
            if confirm:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM editorial WHERE id = %s", (editorial_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Info", "Editorial eliminada correctament.")
                self.refresh_editorial_data()
        else:
            messagebox.showwarning("Atenció", "Selecciona una editorial per eliminar.")

    def go_back(self):
        from classes.admin_dashboard import AdminDashboardFrame
        self.controller.show_frame(AdminDashboardFrame)


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
        self.controller.show_frame(ManageEditorialsFrame)

    def go_back(self):
        self.controller.show_frame(ManageEditorialsFrame)


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

        tk.Button(self, text="Guardar", command=self.update_editorial, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

    def refresh(self, editorial_id):

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
                tk.Label(self.data_frame, text=label, font=("Arial", 14)).grid(row=i, column=0, padx=10, pady=5)
                entry = tk.Entry(self.data_frame, font=("Arial", 14))
                entry.grid(row=i, column=1, padx=10, pady=5)
                entry.insert(0, editorial_data[i])

            self.editorial_id = editorial_data[0]
        else:
            messagebox.showwarning("Atenció", "Editorial no trobada.")
            self.controller.show_frame(ManageEditorialsFrame)

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
        self.controller.show_frame(ManageEditorialsFrame)

    def go_back(self):
        self.controller.show_frame(ManageEditorialsFrame)


# Corrección para ViewEditorialFrame (recibe y utiliza editorial_id)
class ViewEditorialFrame(tk.Frame):
    def __init__(self, parent, controller, editorial_id=None):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Visualitzar Editorial", font=("Arial", 18)).pack(pady=20)

        # Datos cargados
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=10)

        if not editorial_id:
            self.refresh(editorial_id)
            # Botón para volver

        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

    def refresh(self, editorial_id):
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
            for i, value in enumerate(editorial_data):
                tk.Label(self.data_frame, text=f"{data_labels[i]}: {value}", font=("Arial", 14)).pack(anchor="w")
        else:
            messagebox.showwarning("Atenció", "Editorial no trobada.")
            self.controller.show_frame(ManageEditorialsFrame)

    def go_back(self):
        self.controller.show_frame(ManageEditorialsFrame)
