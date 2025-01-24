# classes/register.py
import tkinter as tk
from tkinter import messagebox
from mysql.connector.errors import DatabaseError, InterfaceError
from classes.database import connect_db


class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.refresh()

    def refresh(self):
        from classes.login import LoginFrame  # Importación diferida
        # Limpiar el frame
        for widget in self.winfo_children():
            widget.destroy()

        # Crear los widgets
        tk.Label(self, text="Registrar-se", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Nom", font=("Arial", 14)).pack(pady=5)
        self.name_entry = tk.Entry(self, font=("Arial", 14))
        self.name_entry.pack(pady=5)

        tk.Label(self, text="Usuari", font=("Arial", 14)).pack(pady=5)
        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Contrasenya", font=("Arial", 14)).pack(pady=5)
        self.password_entry = tk.Entry(self, font=("Arial", 14), show="*")
        self.password_entry.pack(pady=5)

        self.is_admin = tk.BooleanVar()
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
            admin_exists = cursor.fetchone()[0] > 0
            conn.close()
        except (DatabaseError, InterfaceError):
            messagebox.showerror("Error de connexió",
                                 "No es pot connectar a la base de dades! Avisa a l'administrador.")
            self.controller.show_frame(LoginFrame)
            return

        if not admin_exists:
            tk.Checkbutton(self, text="Administrador", font=("Arial", 14), variable=self.is_admin).pack(pady=5)

        tk.Button(self, text="Registrar", font=("Arial", 14), command=self.register_user).pack(pady=20)
        tk.Button(self, text="Tornar", command=self.go_to_login).pack()

    def go_to_login(self):
        from classes.login import LoginFrame  # Importación diferida
        self.controller.show_frame(LoginFrame)

    def register_user(self):
        from classes.login import LoginFrame  # Importación diferida
        name = self.name_entry.get()
        is_admin = self.is_admin.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Aquest usuari ja està registrat")
                return
            cursor.execute("INSERT INTO users (name, username, password, is_admin) VALUES (%s, %s, %s, %s)",
                           (name, username, password, is_admin))
            conn.commit()
            messagebox.showinfo("Èxit", "Usuari registrat correctament")
            self.controller.show_frame(LoginFrame)
        except (DatabaseError, InterfaceError):
            messagebox.showerror("Error de connexió",
                                 "No es pot connectar a la base de dades! Avisa a l'administrador.")
            self.controller.show_frame(LoginFrame)
        except Exception as e:
            messagebox.showerror("Error", f"No s'ha pogut registrar l'usuari: {e}")
        finally:
            conn.close()
