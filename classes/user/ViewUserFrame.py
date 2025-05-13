import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db

from classes.user.ViewRentFrame import ViewRentFrame
from classes.user.ViewReservationFrame import ViewReservationFrame


class ViewUserFrame(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.controller = controller

        # Si se proporciona un user_id, refresca la vista
        self.refresh()

    def refresh(self, user_id=None):

        if user_id:
            self.user_id = user_id

        """Refresca la vista del usuario."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Informació de l'Usuari", font=("Arial", 18)).pack(pady=10)

        # 🟢 Treeview para mostrar datos del usuario
        self.tree = ttk.Treeview(self, columns=("id", "name", "username", "is_admin"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nom")
        self.tree.heading("username", text="Usuari")
        self.tree.heading("is_admin", text="Administrador")

        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("username", width=200)
        self.tree.column("is_admin", width=100)

        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        # Botones de acción
        tk.Button(self, text="Llibres Alquilats", command=self.rent_books, font=("Arial", 14)).pack(pady=5)
        tk.Button(self, text="Reserves", command=self.view_reservations, font=("Arial", 14)).pack(pady=5)
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

        # Limpia eventos específicos del Treeview (si existe)
        if hasattr(self, "tree"):
            self.tree.unbind("<Double-1>")
            self.tree.unbind("<Return>")
            self.tree.unbind("<space>")
            self.tree.unbind("<Delete>")

        if not self.user_id:
            messagebox.showerror("Error", "No hi ha cap usuari seleccionat.")
            return

        user = self.controller.get_user_by_id(self.user_id)
        if user:
            self.tree.insert("", "end",
                             values=(user["id"], user["name"], user["username"], "Sí" if user["is_admin"] else "No"))
        else:
            messagebox.showerror("Error", "Usuari no trobat.")

        # Selecciona la fila del Treeview
        for item in self.tree.get_children():
            if self.tree.item(item)["values"][0] == self.user_id:
                self.tree.selection_set(item)
                break

    def go_back(self):
        """Vuelve a la pantalla de gestión de usuarios y refresca la lista."""
        from classes.user.ManageUsersFrame import ManageUsersFrame
        if hasattr(self.controller.frames[ManageUsersFrame], "refresh_user_list"):
            self.controller.frames[ManageUsersFrame].refresh_user_list()
        self.controller.show_frame(ManageUsersFrame)

    def rent_books(self):
        """Muestra los libros alquilados por el usuario."""
        if self.user_id:
            if self.controller.get_rent_books(self.user_id):
                self.controller.show_frame(ViewRentFrame, self.user_id)
            else:
                messagebox.showerror("Error", "Aquest usuari no te cap llibre alquilat.")
        else:
            messagebox.showerror("Error", "No hi ha cap usuari seleccionat.")

    def view_reservations(self):
        """Muestra las reservas hechas por el usuario."""
        if self.user_id:
            if self.controller.get_user_reservations(self.user_id):
                self.controller.show_frame(ViewReservationFrame, self.user_id)
            else:
                messagebox.showerror("Error", "Aquest usuari no ha fet cap reserva.")
        else:
            messagebox.showerror("Error", "No hi ha cap usuari seleccionat.")
