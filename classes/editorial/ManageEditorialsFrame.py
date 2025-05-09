import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from classes.editorial.ViewEditorialFrame import ViewEditorialFrame
from classes.editorial.AddEditorialFrame import AddEditorialFrame
from classes.editorial.EditEditorialFrame import EditEditorialFrame


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
        self.bind_all("<Escape>", lambda e: self.go_back())

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
            self.controller.show_frame(ViewEditorialFrame, editorial_id)

    def add_editorial(self):
        # Navegar al frame para añadir editorial
        self.controller.show_frame(AddEditorialFrame)

    def edit_editorial(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item)["values"]
            editorial_id = item_data[0]
            # Navegar al frame para editar editorial
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

