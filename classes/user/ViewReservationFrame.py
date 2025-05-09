import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db


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

    def go_back(self):
        from classes.user.ViewUserFrame import ViewUserFrame
        """Vuelve a la pantalla de información del usuario."""
        if self.user_id:
            self.controller.show_frame(ViewUserFrame, self.user_id)
        else:
            messagebox.showerror("Error", "No hi ha cap usuari seleccionat.")
