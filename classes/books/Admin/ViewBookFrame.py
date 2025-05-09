import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db

class ViewBookFrame(tk.Frame):
    def __init__(self, parent, controller, book_id=None):
        super().__init__(parent)
        self.controller = controller

        self.book_id = book_id

        tk.Label(self, text="Visualitzar Llibre", font=("Arial", 18)).pack(pady=20)

        # Datos cargados
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=10)

        self.refresh(book_id)

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

        tk.Button(self, text="Alquilar", command=self.rent_book, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Reservar", command=self.reserve_book, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

    def refresh(self, book_id=None):
        conn = connect_db()
        cursor = conn.cursor()

        self.book_id = book_id

        cursor.execute("""
            SELECT b.id, b.title, b.author, g.name AS genre, e.name AS editorial, 
                   b.available_qty, b.reserved
            FROM books b
            LEFT JOIN books_genres bg ON b.id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.id
            LEFT JOIN editorial e ON b.editorial_id = e.id
            WHERE b.id = %s
        """, (self.book_id,))

        book = cursor.fetchone()
        conn.close()

        if book:
            for widget in self.data_frame.winfo_children():
                widget.destroy()

            labels = ["ID", "Títol", "Autor", "Gènere", "Editorial", "Stock disponible", "Reservats"]
            for i, value in enumerate(book):
                tk.Label(self.data_frame, text=f"{labels[i]}: {value}", font=("Arial", 14)).pack()

    def go_back(self):
        from classes.books.Admin.ManageBooksFrame import ManageBooksFrame
        self.controller.show_frame(ManageBooksFrame)
        self.controller.frames[ManageBooksFrame].refresh()

    def rent_book(self, book_id=None):
        rent_book_id = self.book_id
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT available_qty FROM books WHERE id = %s", (rent_book_id,))
        available_qty = cursor.fetchone()
        conn.close()

        if available_qty[0] > 0:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO rents (book_id, user_id) VALUES (%s, %s)",
                           (rent_book_id, self.controller.current_user[0]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Info", "Llibre llogat correctament.")
            self.refresh()
        else:
            messagebox.showwarning("Error", "El llibre seleccionat no está disponible, automàticament s'ha reservat.")
            self.reserve_book()

    def reserve_book(self):
        reserve_book_id = self.book_selected_user()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT available_qty FROM books WHERE id = %s", (reserve_book_id,))
        available_qty = cursor.fetchone()
        conn.close()

        if available_qty > 0:
            messagebox.showwarning("Atenció", "El llibre seleccionat està disponible, automàticament s'ha llogat.")
            self.rent_book()
        else:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reservations (book_id, user_id) VALUES (%s, %s)",
                           (reserve_book_id, self.controller.current_user[0]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Info", "Llibre reservat correctament.")
            self.refresh()


def get_genre(book_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT genre_id FROM books_genres WHERE book_id = %s", (book_id,))
    genre_id = cursor.fetchone()
    if genre_id:
        cursor.execute("SELECT name FROM genres WHERE id = %s", (genre_id[0],))
        genre = cursor.fetchone()
        conn.close()
        return genre[0] if genre else None
    conn.close()
    return None


def get_editorials():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM editorial")
    editorials = cursor.fetchall()
    conn.close()

    return [f"{editorial[0]} - {editorial[1]}" for editorial in editorials]


def get_editorial_name(editorial_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM editorial WHERE id = %s", (editorial_id,))
    editorial_name = cursor.fetchone()
    conn.close()
    return editorial_name[0]

