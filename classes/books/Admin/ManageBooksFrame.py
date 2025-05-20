import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from datetime import datetime
from classes.books.Admin.EditBookFrame import EditBookFrame
from classes.books.Admin.ViewBookFrame import ViewBookFrame
from classes.books.Admin.AddBookFrame import AddBookFrame
from classes.books.Admin.DeleteBookFrame import DeleteBookFrame


class ManageBooksFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Gestionar Llibres", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Llibres (seleccioneu un llibre per gestionar)", font=("Arial", 14)).pack()

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Configuración del Treeview
        self.tree = ttk.Treeview(
            container,
            columns=("id", "title", "author", "genre", "editorial", "available_qty", "reserved"),
            show="headings",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Títol")
        self.tree.heading("author", text="Autor")
        self.tree.heading("genre", text="Gènere")
        self.tree.heading("editorial", text="Editorial")
        self.tree.heading("available_qty", text="Stock Disponible")
        self.tree.heading("reserved", text="Reservats")

        self.tree.column("id", width=40)
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=150)
        self.tree.column("editorial", width=150)
        self.tree.column("available_qty", width=100)
        self.tree.column("reserved", width=100)

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 🟢 Bindings para eventos
        self.tree.bind("<Double-1>", self.book_selected)
        self.tree.bind("<Return>", self.book_selected)
        self.tree.bind("<space>", self.book_selected)
        self.tree.bind("<Delete>", lambda e: self.delete_book())
        self.bind_all("<Escape>", lambda e: self.go_back())

        # Botones de acción
        tk.Button(self, text="Visualitzar Llibre", command=self.book_selected, font=("Arial", 14)).pack(pady=10,
                                                                                                        padx=10,
                                                                                                        anchor="w",
                                                                                                        side="left")
        tk.Button(self, text="Afegir Llibre", command=self.add_book, font=("Arial", 14)).pack(pady=10, padx=10,
                                                                                              anchor="w", side="left")
        tk.Button(self, text="Editar Llibre", command=self.edit_book, font=("Arial", 14)).pack(pady=10, padx=10,
                                                                                               anchor="w", side="left")
        tk.Button(self, text="Eliminar Llibre", command=self.delete_book, font=("Arial", 14)).pack(pady=10, padx=10,
                                                                                                   anchor="w",
                                                                                                   side="left")
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10, padx=10, anchor="w",
                                                                                      side="left")

        # Cargar datos
        self.refresh()

    def refresh(self):
        """Carga todos los libros con una consulta optimizada."""
        self.tree.delete(*self.tree.get_children())

        # Limpiar el book_id

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                b.id, b.title, b.author, g.name AS genre, e.name AS editorial, 
                b.available_qty, b.reserved
            FROM books b
            LEFT JOIN books_genres bg ON b.id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.id
            LEFT JOIN editorial e ON b.editorial_id = e.id
        """)

        books = cursor.fetchall()
        conn.close()

        for book in books:
            self.tree.insert("", "end", values=book)

        if books:
            first_item = self.tree.get_children()[0]
            self.tree.focus_set()
            self.tree.selection_set(first_item)
            self.tree.focus(first_item)
            self.tree.see(first_item)

    @staticmethod
    def get_genre(book_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT genre_id FROM books_genres WHERE book_id = %s", (book_id,))
        genre_id = cursor.fetchone()
        cursor.execute("SELECT name FROM genres WHERE id = %s", (genre_id[0],))
        genre = cursor.fetchone()
        conn.close()
        return genre[0]

    @staticmethod
    def get_editorial_name(editorial_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM editorial WHERE id = %s", (editorial_id,))
        editorial_name = cursor.fetchone()
        conn.close()
        return editorial_name[0]

    def book_selected(self, event=None):
        selected_item = self.tree.selection()
        if selected_item:
            book_id = self.tree.item(selected_item)["values"][0]
            self.controller.show_frame(ViewBookFrame, book_id)

    def add_book(self):
        # Navegar al frame para añadir libro
        self.controller.show_frame(AddBookFrame)

    def edit_book(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item)["values"]
            book_id = item_data[0]
            # Navegar al frame para editar libro
            self.controller.show_frame(EditBookFrame, book_id)
        else:
            messagebox.showwarning("Atenció", "Selecciona un llibre per editar.")

    def delete_book(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenció", "Selecciona un llibre per eliminar.")
            return

        book_id = self.tree.item(selected_item)["values"][0]

        confirm = messagebox.askyesno("Eliminar Llibre", "Estàs segur que vols eliminar aquest llibre?")
        if confirm:
            conn = connect_db()
            cursor = conn.cursor()
            try:
                # Delete dependent rows in the rents table
                cursor.execute("DELETE FROM rents WHERE book_id = %s", (book_id,))
                # Delete the book
                cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
                conn.commit()
                messagebox.showinfo("Info", "Llibre eliminat correctament.")
                self.refresh()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"S'ha produït un error: {e}")
            finally:
                conn.close()

    def go_back(self):
        from classes.admin_dashboard import AdminDashboardFrame
        self.controller.show_frame(AdminDashboardFrame)
