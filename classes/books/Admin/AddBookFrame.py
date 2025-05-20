import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db
from classes.books.Admin.EditBookFrame import EditBookFrame


class AddBookFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.genres = []  # Cache for genres
        self.editorials = []  # Cache for editorials

        tk.Label(self, text="Afegir Llibre", font=("Arial", 18)).pack(pady=20)

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

        tk.Button(self, text="Afegir", command=self.add_new_book, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack()

        # Load genres and editorials into the Comboboxes
        EditBookFrame.load_genres_and_editorials(self)

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

    def add_new_book(self):
        book_data = {field: widget.get() for field, (_, widget) in self.fields.items()}

        # Validate that all fields are filled
        if not all(book_data.values()):
            messagebox.showerror("Error", "Tots els camps són obligatoris.")
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Insert the new book into the database
            cursor.execute(
                """
                INSERT INTO books (title, author, available_qty, editorial_id)
                VALUES (%s, %s, %s, (SELECT id FROM editorial WHERE CONCAT(id, ' - ', name) = %s))
                """,
                (
                    book_data["title"],
                    book_data["author"],
                    book_data["available"],
                    book_data["editorial"],
                ),
            )

            # Get the ID of the newly inserted book
            book_id = cursor.lastrowid

            # Insert the genre into the books_genres table
            cursor.execute(
                """
                INSERT INTO books_genres (book_id, genre_id)
                SELECT %s, id FROM genres WHERE name = %s
                """,
                (book_id, book_data["genre"]),
            )

            conn.commit()
            messagebox.showinfo("Afegir Llibre", "Llibre afegit correctament.")
            self.go_back()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"S'ha produït un error: {e}")

        finally:
            conn.close()

    def go_back(self):
        from classes.books.Admin.ManageBooksFrame import ManageBooksFrame
        self.controller.show_frame(ManageBooksFrame)
        self.controller.frames[ManageBooksFrame].refresh()
