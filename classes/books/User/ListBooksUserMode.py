import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from datetime import datetime
from classes.books.User.ViewBookFrameUserMode import ViewBookFrameUserMode
from classes.books.User.ListRentedBooks import ListRentedBooks
from classes.books.User.ListReservedBooks import ListReservedBooks


class ListBooksUserMode(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.book_id = None

        tk.Label(self, text="Llistat de Llibres", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Llibres (seleccioneu un llibre)", font=("Arial", 14)).pack()

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            container,
            columns=("id", "title", "author", "genre", "editorial", "available_qty", "reserved"),
            show="headings",
        )
        for col in ["id", "title", "author", "genre", "editorial", "available_qty", "reserved"]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(self, text="Visualitzar Llibre", command=self.book_selected, font=("Arial", 14)).pack(pady=10,
                                                                                                        side="left")
        tk.Button(self, text="Alquilar Llibre", command=self.rent_book, font=("Arial", 14)).pack(pady=10, side="left")
        tk.Button(self, text="Reservar Llibre", command=self.reserve_book, font=("Arial", 14)).pack(pady=10,
                                                                                                    side="left")
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10, side="left")

        self.refresh()

    def refresh(self):
        """Carga la lista de libros en la interfaz."""
        self.tree.delete(*self.tree.get_children())

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author, g.name AS genre, e.name AS editorial, 
                   b.available_qty, b.reserved
            FROM books b
            LEFT JOIN books_genres bg ON b.id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.id
            LEFT JOIN editorial e ON b.editorial_id = e.id
        """)

        for book in cursor.fetchall():
            self.tree.insert("", "end", values=book)

        conn.close()

    def book_selected(self):
        selected_item = self.tree.selection()
        if selected_item:
            book_id = self.tree.item(selected_item)["values"][0]
            self.controller.show_frame(ViewBookFrameUserMode, book_id)

    def rent_book(self):
        """Alquila el libro seleccionado directamente."""
        selected_item = self.tree.selection()
        if selected_item:
            book_id = self.tree.item(selected_item)["values"][0]

            # 🟢 Llamar directamente a la función de alquiler
            frame = ViewBookFrameUserMode(self, self.controller, book_id)
            frame.rent_book()
            self.refresh()

    def reserve_book(self):
        """Reserva el libro seleccionado directamente."""
        selected_item = self.tree.selection()
        if selected_item:
            book_id = self.tree.item(selected_item)["values"][0]

            # 🟢 Llamar directamente a la función de reserva
            frame = ViewBookFrameUserMode(self, self.controller, book_id)
            frame.reserve_book()
            self.refresh()

    def go_back(self):
        from classes.user_dashboard import UserDashboardFrame
        self.controller.show_frame(UserDashboardFrame)
