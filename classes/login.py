# classes/login.py
import tkinter as tk
from tkinter import messagebox
from mysql.connector.errors import DatabaseError, InterfaceError
from classes.admin_dashboard import AdminDashboardFrame
from classes.user_dashboard import UserDashboardFrame
from classes.database import connect_db


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.refresh()

    def refresh(self):
        # Limpiar el frame
        for widget in self.winfo_children():
            widget.destroy()
        # Crear los widgets
        tk.Label(self, text="Inicia Sessió", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Usuari:", font=("Arial", 14)).pack()
        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.pack()

        tk.Label(self, text="Contrasenya:", font=("Arial", 14)).pack()
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 14))
        self.password_entry.pack()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        tk.Button(self, text="Login", command=self.login, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Registrar-se", command=self.go_to_register, font=("Arial", 14)).pack()
        tk.Button(self, text="Sortir", command=self.controller.quit, font=("Arial", 14)).pack(pady=10)

    def go_to_register(self):
        from classes.register import RegisterFrame  # Importación diferida
        self.controller.show_frame(RegisterFrame)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, username, is_admin FROM users WHERE username = %s AND password = %s",
                           (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                self.controller.current_user = user  # Save the authenticated user's information
                user_id = user[0]

                self.controller.check_and_notify_user_reservations(user_id)  # Check if the user has any reservations

                if user[3]:  # Check if the user is an admin
                    self.controller.show_frame(AdminDashboardFrame, user[1])
                else:
                    self.controller.show_frame(UserDashboardFrame, user[1])
            else:
                messagebox.showerror("Error", "Credencials incorrectes. Torna a intentar-ho.")
        except (DatabaseError, InterfaceError):
            if not self.controller.connection_error:
                self.controller.connection_error = True
                messagebox.showerror("Error de connexió",
                                     "Error de connexió no es pot connectar a la base de dades! Avisa a "
                                     "l'administrador.")
                self.controller.show_frame(LoginFrame)
