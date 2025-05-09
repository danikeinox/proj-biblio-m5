import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db
from classes.user.AddUserFrame import AddUserFrame
from classes.user.EditUserFrame import EditUserFrame
from classes.user.ViewUserFrame import ViewUserFrame
from classes.user.ViewReservationFrame import ViewReservationFrame
from classes.user.ViewRentFrame import ViewRentFrame


class ManageUsersFrame(tk.Frame):
    def __init__(self, parent, controller):
        from classes.admin_dashboard import AdminDashboardFrame
        super().__init__(parent)
        self.controller = controller
        self.users = []
        self.user_id = None

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

        # 🟢 Bindings para eventos
        self.tree.bind("<Double-1>", self.view_user)
        self.tree.bind("<Return>", self.view_user)
        self.tree.bind("<space>", self.view_user)
        self.tree.bind("<Delete>", lambda e: self.delete_user())
        self.bind_all("<Escape>", lambda e: controller.show_frame(AdminDashboardFrame))

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

    def view_user(self, event=None):
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

        self.user_id = self.tree.item(selected_item[0])["values"][0]
        self.controller.show_frame(EditUserFrame, self.user_id)

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
