import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db
import mysql.connector  # Asegúrate de usar el conector adecuado para tu base de datos


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
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack()

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

    def refresh(self):
        # Limpiar los campos de entrada
        self.name_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.conf_password_entry.delete(0, tk.END)
        self.is_admin.set(False)

    def create_user(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        conf_password = self.conf_password_entry.get()
        is_admin = self.is_admin.get()

        # Validaciones iniciales
        if not name or not username or not password:
            messagebox.showerror("Error", "Tots els camps són obligatoris.")
            return
        if password != conf_password:
            messagebox.showerror("Error", "Les contrasenyes no coincideixen.")
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Intentar insertar el nuevo usuario
            cursor.execute(
                "INSERT INTO users (name, username, password, is_admin) VALUES (%s, %s, %s, %s)",
                (name, username, password, is_admin),
            )
            conn.commit()
            messagebox.showinfo("Èxit", "Usuari creat correctament.")
            self.go_back()

        except mysql.connector.IntegrityError as e:
            # Manejar errores de integridad, como duplicados
            if "Duplicate entry" in str(e):
                messagebox.showerror("Error", "El nom d'usuari ja existeix. Tria un altre.")
            else:
                messagebox.showerror("Error", f"S'ha produït un error de base de dades: {e}")
            conn.rollback()
        except Exception as e:
            # Manejar otros errores inesperados
            messagebox.showerror("Error", f"S'ha produït un error inesperat: {e}")
            conn.rollback()
        finally:
            conn.close()

    def go_back(self):
        from classes.user.ManageUsersFrame import ManageUsersFrame
        self.controller.frames[ManageUsersFrame].refresh_user_list()
        self.controller.show_frame(ManageUsersFrame)
