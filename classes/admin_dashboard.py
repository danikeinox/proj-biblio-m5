import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db
from classes.books import ManageBooksFrame
from classes.editorial import ManageEditorialsFrame
from classes.user import ManageUsersFrame, ViewUserFrame, AddUserFrame, EditUserFrame, ViewReservationFrame, \
    ViewRentFrame


class AdminDashboardFrame(tk.Frame):
    def __init__(self, parent, controller, name):
        super().__init__(parent)
        self.name = name
        self.controller = controller

        tk.Label(self, text=f"Benvingut Administrador: {self.name}", font=("Arial", 18)).pack(pady=20)
        tk.Button(self, text="Gestionar editorial", command=self.manage_editorial, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Gestionar llibres", command=self.add_book, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Gestionar Usuaris", command=self.manage_users, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Tancar Sessió", command=self.controller.logout, font=("Arial", 14)).pack(pady=10)

    def refresh_user_data(self):
        if not self.controller.current_user:
            messagebox.showerror("Error", "Sessió no iniciada. Torna a iniciar sessió.")
            self.go_to_login()
            return
        self.name = self.controller.current_user[1]
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text=f"Benvingut Administrador: {self.name}", font=("Arial", 18)).pack(pady=20)
        tk.Button(self, text="Gestionar editorial", command=self.manage_editorial, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Gestionar llibres", command=self.manage_books, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Gestionar Usuaris", command=self.manage_users, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Tancar Sessió", command=self.controller.logout, font=("Arial", 14)).pack(pady=10)

    def manage_editorial(self):
        self.controller.show_frame(ManageEditorialsFrame)

        #  messagebox.showinfo("Afegir Editorial", "Funcionalitat pendent d'implementar.")

    def manage_books(self):
        self.controller.show_frame(ManageBooksFrame)

    def add_book(self):
        conn = connect_db()
        cursor = conn.cursor()

        # Optimizar consultas y unirlas en una sola si es posible
        cursor.execute("""
            SELECT l.id, l.name, e.id, e.name, b.id, b.title, b.author, b.genre, b.available
            FROM books b
            LEFT JOIN libraries l ON b.library_id = l.id
            LEFT JOIN editorials e ON b.editorial_id = e.id
        """)

        data = cursor.fetchall()
        conn.close()

        # Separar los datos por tipo
        libraries = {(row[0], row[1]) for row in data}
        editorials = {(row[2], row[3]) for row in data}
        books = [(row[4], row[5], row[6], row[7], row[8]) for row in data]

        self.controller.show_frame(AddBookFrame)
        frame = self.controller.frames[AddBookFrame]
        frame.update_content(libraries, editorials, books)

    def manage_users(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, is_admin FROM users")
        users = cursor.fetchall()
        conn.close()

        self.controller.show_frame(ManageUsersFrame)
        frame = self.controller.frames[ManageUsersFrame]
        frame.update_content(users)
