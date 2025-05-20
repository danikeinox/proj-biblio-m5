import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db


class EditBookFrame(tk.Frame):
    def __init__(self, parent, controller, book_id=None):
        super().__init__(parent)
        self.controller = controller
        self.book_id = book_id

        self.fields = None
        self.genres = []  # Cache for genres
        self.editorials = []  # Cache for editorials

        self.refresh_book_data(self.book_id)

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

    def refresh_book_data(self, book_id):
        # Actualiza el book_id
        self.book_id = book_id

        # Limpiar la interfaz
        for widget in self.winfo_children():
            widget.destroy()

        # Inicializar la interfaz
        tk.Label(self, text="Editar Llibre", font=("Arial", 18)).pack(pady=20)

        self.fields = {
            "title": ("Títol", tk.Entry(self, font=("Arial", 14))),
            "author": ("Autor", tk.Entry(self, font=("Arial", 14))),
            "genre": ("Gènere", ttk.Combobox(self, font=("Arial", 14))),
            "available": ("Stock Disponible", tk.Entry(self, font=("Arial", 14))),
            "editorial": ("Editorial", ttk.Combobox(self, font=("Arial", 14))),
        }

        for field, (label, widget) in self.fields.items():
            tk.Label(self, text=label, font=("Arial", 14)).pack()
            widget.pack()

        tk.Button(self, text="Editar", command=self.edit_book, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

        # Cargar datos del libro y rellenar los campos
        if self.book_id:
            self.load_book_data()

        # Cargar géneros y editoriales en los Comboboxes
        self.load_genres_and_editorials()

    @staticmethod
    def load_genres_and_editorials(self):

        """Loads genres and editorials in a single query to optimize performance."""

        conn = connect_db()
        cursor = conn.cursor()

        # Fetch genres and editorials in one query
        cursor.execute("""
                SELECT 
                    (SELECT GROUP_CONCAT(name) FROM genres) AS genres,
                    (SELECT GROUP_CONCAT(CONCAT(id, ' - ', name)) FROM editorial) AS editorials
            """)
        result = cursor.fetchone()
        conn.close()

        # Parse results
        self.genres = result[0].split(",") if result[0] else []
        self.editorials = result[1].split(",") if result[1] else []

        # Populate Comboboxes
        genre_widget = self.fields["genre"][1]
        genre_widget["values"] = self.genres

        editorial_widget = self.fields["editorial"][1]
        editorial_widget["values"] = self.editorials

    @staticmethod
    def load_book_data(self):

        """Loads book details, genre, and editorial in a single query."""
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch all book details in one query
        cursor.execute("""
                SELECT 
                    b.title, b.author, b.available_qty, 
                    g.name AS genre, 
                    e.name AS editorial
                FROM books b
                LEFT JOIN books_genres bg ON b.id = bg.book_id
                LEFT JOIN genres g ON bg.genre_id = g.id
                LEFT JOIN editorial e ON b.editorial_id = e.id
                WHERE b.id = %s
            """, (self.book_id,))
        book_data = cursor.fetchone()
        conn.close()

        # Populate fields
        if book_data:
            self.fields["title"][1].insert(0, book_data[0])
            self.fields["author"][1].insert(0, book_data[1])
            self.fields["available"][1].insert(0, book_data[2])

            genre_widget = self.fields["genre"][1]
            genre_widget.set(book_data[3] if book_data[3] else "")

            editorial_widget = self.fields["editorial"][1]
            editorial_widget.set(book_data[4] if book_data[4] else "")

    def edit_book(self):

        """Handles the book editing logic."""
        book_data = {field: widget.get() for field, (_, widget) in self.fields.items()}

        if not self.book_id:
            messagebox.showerror("Error", "Selecciona un llibre abans d'editar.")
            return

        conn = connect_db()
        cursor = conn.cursor()

        # Update book details
        cursor.execute("""
                UPDATE books
            SET title = %s, author = %s, available_qty = %s, editorial_id = (
                    SELECT id FROM editorial WHERE CONCAT(id, ' - ', name) = %s
                )
                WHERE id = %s
            """, (
            book_data["title"],
            book_data["author"],
            book_data["available"],
            book_data["editorial"],
            self.book_id,
        ))

        # Update genre
        cursor.execute("DELETE FROM books_genres WHERE book_id = %s", (self.book_id,))
        cursor.execute("""
                INSERT INTO books_genres (book_id, genre_id)
                SELECT %s, id FROM genres WHERE name = %s
            """, (self.book_id, book_data["genre"]))

        conn.commit()
        conn.close()

        messagebox.showinfo("Editar Llibre", "Llibre editat correctament.")
        self.go_back()

    def go_back(self):
        """Navigates back to the ManageBooksFrame."""
        from classes.books.Admin.ManageBooksFrame import ManageBooksFrame
        self.controller.show_frame(ManageBooksFrame)
        self.controller.frames[ManageBooksFrame].refresh()
