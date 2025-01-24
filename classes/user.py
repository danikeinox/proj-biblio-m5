import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db


class ManageUsersFrame(tk.Frame):
    def __init__(self, parent, controller):
        from classes.admin_dashboard import AdminDashboardFrame
        super().__init__(parent)
        self.controller = controller
        self.users = []

        tk.Label(self, text="Gestionar Usuaris", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Usuaris (seleccioneu un usuari)", font=("Arial", 11)).pack(padx=10, pady=10)

        # 🟢 Contenedor para Treeview y Scrollbar
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # 🟢 Definir Treeview con columnas
        self.tree = ttk.Treeview(
            container,
            columns=("id", "name", "username", "is_admin"),
            show="headings",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nom")
        self.tree.heading("username", text="Usuari")
        self.tree.heading("is_admin", text="Administrador")

        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("username", width=200)
        self.tree.column("is_admin", width=100)

        self.tree.pack(side="left", fill="both", expand=True)

        # 🟢 Scrollbar para Treeview
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 🟢 Botones de acción
        tk.Button(self, text="Veure informació", command=self.view_user, font=("Arial", 14)).pack(pady=5)
        tk.Button(self, text="Editar Usuari", command=self.edit_user, font=("Arial", 14)).pack(pady=5)
        tk.Button(self, text="Afegir Usuari", command=self.add_user, font=("Arial", 14)).pack(pady=5)
        tk.Button(self, text="Eliminar Usuari", command=self.delete_user, font=("Arial", 14)).pack(pady=5)
        tk.Button(self, text="Tornar", command=lambda: controller.show_frame(AdminDashboardFrame),
                  font=("Arial", 14)).pack(pady=5)

        self.refresh_user_list()

    def update_content(self, users):
        self.users = users
        self.refresh_user_list()

    def refresh_user_list(self):
        """Refresca la lista de usuarios."""
        self.tree.delete(*self.tree.get_children())

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, is_admin FROM users")
        self.users = cursor.fetchall()
        conn.close()

        for user in self.users:
            self.tree.insert("", "end", values=(user[0], user[1], user[2], "Sí" if user[3] else "No"))

    def add_user(self):
        """Cambia al marco para agregar usuario."""
        self.controller.show_frame(AddUserFrame)

    def view_user(self):
        """Muestra la información del usuario seleccionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccioneu un usuari per veure la informació.")
            return

        user_id = self.tree.item(selected_item[0])["values"][0]
        self.controller.show_frame(ViewUserFrame, user_id)

    def edit_user(self):
        """Edita un usuario seleccionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccioneu un usuari per editar.")
            return

        user_id = self.tree.item(selected_item[0])["values"][0]
        self.controller.show_frame(EditUserFrame, user_id)

    def delete_user(self):
        selected_index = self.tree.selection()
        if not selected_index:
            messagebox.showerror("Error", "Seleccioneu un usuari per eliminar")
            return

        selected_user = self.tree.item(selected_index[0])  # Obtener el usuario seleccionado
        user_id = selected_user["values"][0]  # Asume que el ID del usuario está en la primera posición
        is_admin = selected_user["values"][3]  # Asume que el campo de administrador está en la quinta posición

        if not self.controller.current_user:
            messagebox.showerror("Error", "Sessió no iniciada. Torna a iniciar sessió.")
            return

        if self.controller.current_user[0] == user_id:
            messagebox.showerror("Error", "No pots eliminar el teu propi usuari")
            return

        confirm = messagebox.askyesno("Confirmar", f"Vols eliminar l'usuari {selected_user['values'][1]}?")
        if confirm:
            conn = connect_db()
            cursor = conn.cursor()

            if is_admin == "Sí":
                messagebox.showwarning("Atenció", "Aquest usuari és administrador.")
                confirm = messagebox.askyesno("Confirmar", "Vols eliminar-lo igualment?")
                if not confirm:
                    return

            cursor.execute("SELECT COUNT(*) FROM rents WHERE user_id = %s", (user_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Atenció", "Aquest usuari té llibres alquilats.")
                confirm = messagebox.askyesno("Confirmar", "Vols eliminar-lo igualment?")
                if confirm:
                    cursor.execute("DELETE FROM rents WHERE user_id = %s", (user_id,))
                    conn.commit()

            cursor.execute("SELECT COUNT(*) FROM reservations WHERE user_id = %s", (user_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Atenció", "Aquest usuari té reserves associades.")
                confirm = messagebox.askyesno("Confirmar", "Vols eliminar-lo igualment?")
                if confirm:
                    cursor.execute("DELETE FROM reservations WHERE user_id = %s", (user_id,))
                    conn.commit()

            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Èxit", f"L'usuari {selected_user['values'][1]} ha estat eliminat")

        self.refresh_user_list()


class ViewUserFrame(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id

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

        # Si se proporciona un user_id, refresca la vista
        if user_id:
            self.refresh_user(user_id)

    def refresh_user(self, user_id):
        """Actualiza la información del usuario en la vista."""
        self.tree.delete(*self.tree.get_children())  # Limpiar datos previos
        self.user_id = user_id

        user = self.controller.get_user_by_id(user_id)
        if user:
            self.tree.insert("", "end",
                             values=(user["id"], user["name"], user["username"], "Sí" if user["is_admin"] else "No"))
        else:
            messagebox.showerror("Error", "Usuari no trobat.")

    def go_back(self):
        """Vuelve a la pantalla de gestión de usuarios y refresca la lista."""
        from classes.user import ManageUsersFrame
        self.controller.show_frame(ManageUsersFrame)
        if hasattr(self.controller.frames[ManageUsersFrame], "refresh_user_list"):
            self.controller.frames[ManageUsersFrame].refresh_user_list()

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


class ViewRentFrame(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id

        tk.Label(self, text="Llibres Alquilats", font=("Arial", 18)).pack(pady=10)

        # 🟢 Contenedor para Treeview y Scrollbar
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # 🟢 Treeview para mostrar alquileres
        self.tree = ttk.Treeview(
            container,
            columns=("id", "title", "author", "time_rented", "status"),
            show="headings",
        )
        self.tree.heading("id", text="ID Llibre")
        self.tree.heading("title", text="Títol")
        self.tree.heading("author", text="Autor")
        self.tree.heading("time_rented", text="Data Lloguer")
        self.tree.heading("status", text="Estat")

        self.tree.column("id", width=50)
        self.tree.column("title", width=150)
        self.tree.column("author", width=150)
        self.tree.column("time_rented", width=120)
        self.tree.column("status", width=100)

        self.tree.pack(side="left", fill="both", expand=True)

        # 🟢 Scrollbar para Treeview
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

        if user_id:
            self.refresh(user_id)

    def refresh(self, user_id):
        """Carga los alquileres del usuario."""
        self.tree.delete(*self.tree.get_children())
        self.user_id = user_id

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.book_id, b.title, b.author, r.time_rented, r.status
            FROM rents r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = %s
        """, (user_id,))
        rents = cursor.fetchall()
        conn.close()

        for rent in rents:
            self.tree.insert("", "end", values=rent)

    def go_back(self):
        """Vuelve a la pantalla de información del usuario."""
        if self.user_id:
            self.controller.show_frame(ViewUserFrame, self.user_id)
        else:
            messagebox.showerror("Error", "No hi ha cap usuari seleccionat.")


class ViewReservationFrame(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.controller = controller
        self.user_id = user_id

        tk.Label(self, text="Reserves", font=("Arial", 18)).pack(pady=10)

        # 🟢 Contenedor para Treeview y Scrollbar
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # 🟢 Treeview para mostrar reservas
        self.tree = ttk.Treeview(
            container,
            columns=("id", "title", "author", "time_reserved", "status"),
            show="headings",
        )
        self.tree.heading("id", text="ID Llibre")
        self.tree.heading("title", text="Títol")
        self.tree.heading("author", text="Autor")
        self.tree.heading("time_reserved", text="Data Reserva")
        self.tree.heading("status", text="Estat")

        self.tree.column("id", width=50)
        self.tree.column("title", width=150)
        self.tree.column("author", width=150)
        self.tree.column("time_reserved", width=120)
        self.tree.column("status", width=100)

        self.tree.pack(side="left", fill="both", expand=True)

        # 🟢 Scrollbar para Treeview
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

        if user_id:
            self.refresh(user_id)

    def refresh(self, user_id):
        """Carga las reservas del usuario."""
        self.tree.delete(*self.tree.get_children())
        self.user_id = user_id

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.book_id, b.title, b.author, r.time_reserved, r.status
            FROM reservations r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = %s
        """, (user_id,))
        reservations = cursor.fetchall()
        conn.close()

        for reservation in reservations:
            self.tree.insert("", "end", values=reservation)

    def go_back(self):
        """Vuelve a la pantalla de información del usuario."""
        if self.user_id:
            self.controller.show_frame(ViewUserFrame, self.user_id)
        else:
            messagebox.showerror("Error", "No hi ha cap usuari seleccionat.")


class EditUserFrame(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.controller = controller

        tk.Label(self, text="Editar Usuari", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Nom", font=("Arial", 14)).pack()
        self.name_entry = tk.Entry(self, font=("Arial", 14))
        self.name_entry.pack()

        tk.Label(self, text="Usuari", font=("Arial", 14)).pack()
        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.pack()

        self.is_admin = tk.BooleanVar()
        tk.Checkbutton(self, text="Administrador", font=("Arial", 14)).pack()

        tk.Button(self, text="Desar", command=self.save_user, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack()

    def refresh(self, user_id):
        self.name_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.is_admin.set(False)
        user = self.controller.get_user_by_id(user_id)
        self.name_entry.insert(0, user["name"])
        self.username_entry.insert(0, user["username"])
        self.is_admin.set(user["is_admin"])
        self.user_id = user["id"]

    def save_user(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        is_admin = self.is_admin.get()
        user_id = self.user_id

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = %s, username = %s, is_admin = %s WHERE id = %s",
            (name, username, is_admin, user_id),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Èxit", "Usuari actualitzat correctament.")
        self.controller.frames[ManageUsersFrame].refresh_user_list()
        self.controller.show_frame(ManageUsersFrame)

    def go_back(self):
        self.controller.show_frame(ManageUsersFrame)


class AddUserFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Afegir Usuari", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Nom", font=("Arial", 14)).pack()
        self.name_entry = tk.Entry(self, font=("Arial", 14))
        self.name_entry.pack()

        tk.Label(self, text="Usuari", font=("Arial", 14)).pack()
        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.pack()

        tk.Label(self, text="Contrasenya", font=("Arial", 14)).pack()
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 14))
        self.password_entry.pack()

        tk.Label(self, text="Confirmar Contrasenya", font=("Arial", 14)).pack()
        self.conf_password_entry = tk.Entry(self, show="*", font=("Arial", 14))
        self.conf_password_entry.pack()

        self.is_admin = tk.BooleanVar()
        tk.Checkbutton(self, text="Administrador", variable=self.is_admin, font=("Arial", 14)).pack()

        tk.Button(self, text="Registrar", command=self.create_user, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=lambda: controller.show_frame(ManageUsersFrame),
                  font=("Arial", 14)).pack()

    def create_user(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        conf_password = self.conf_password_entry.get()
        is_admin = self.is_admin.get()

        if not name or not username or not password:
            messagebox.showerror("Error", "Tots els camps són obligatoris.")
            return
        if password != conf_password:
            messagebox.showerror("Error", "Les contrasenyes no coincideixen.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, username, password, is_admin) VALUES (%s, %s, %s, %s)",
            (name, username, password, is_admin),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Èxit", "Usuari creat correctament.")
        self.controller.frames[ManageUsersFrame].refresh_user_list()
        self.controller.show_frame(ManageUsersFrame)

    def go_back(self):
        self.controller.show_frame(ManageUsersFrame)
