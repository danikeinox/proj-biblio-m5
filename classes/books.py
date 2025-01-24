import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from datetime import datetime


# ADMIN MODE
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
        self.tree.heading("available_qty", text="Quantitat Disponible")
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

        # Eventos
        self.tree.bind("<Double-1>", self.book_selected)
        self.tree.bind("<Return>", self.book_selected)
        self.tree.bind("<space>", self.book_selected)
        self.tree.bind("<Delete>", lambda e: self.delete_book())
        self.tree.bind("<Escape>", lambda e: self.controller.show_frame(ManageBooksFrame))

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
        from classes.books import AddBookFrame
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
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Info", "Llibre eliminat correctament.")
            self.refresh()

    def go_back(self):
        from classes.admin_dashboard import AdminDashboardFrame
        self.controller.show_frame(AdminDashboardFrame)


# Clases para la gestión de libros
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

            labels = ["ID", "Títol", "Autor", "Gènere", "Editorial", "Quantitat disponible", "Reservats"]
            for i, value in enumerate(book):
                tk.Label(self.data_frame, text=f"{labels[i]}: {value}", font=("Arial", 14)).pack()

    def go_back(self):
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
            messagebox.showerror("Error", "El llibre seleccionat no está disponible, automàticament s'ha reservat.")
            self.reserve_book()

    def reserve_book(self):
        reserve_book_id = self.book_selected_user()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT reserved FROM books WHERE id = %s", (reserve_book_id,))
        reserved = cursor.fetchone()
        cursor.execute("SELECT available_qty FROM books WHERE id = %s", (reserve_book_id,))
        available_qty = cursor.fetchone()
        conn.close()

        if available_qty > 0:
            tk.messagebox.showwarning("Atenció", "El llibre seleccionat està disponible, automàticament s'ha llogat.")
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


class EditBookFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Editar Llibre", font=("Arial", 18)).pack(pady=20)

        self.fields = {
            "title": ("Títol", tk.Entry(self, font=("Arial", 14))),
            "author": ("Autor", tk.Entry(self, font=("Arial", 14))),
            "genre": ("Gènere", tk.Entry(self, font=("Arial", 14))),
            "available": ("Disponible", tk.Entry(self, font=("Arial", 14))),
            "library": ("Llibreria", ttk.Combobox(self, font=("Arial", 14))),
            "editorial": ("Editorial", ttk.Combobox(self, font=("Arial", 14))),
        }

        for field, (label, widget) in self.fields.items():
            tk.Label(self, text=label, font=("Arial", 14)).pack()
            widget.pack()

        tk.Button(self, text="Editar", command=self.edit_book, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

    def edit_book(self):
        book_data = {field: widget.get() for field, (_, widget) in self.fields.items()}
        selected_book_id = self.controller.selected_book_id

        if not selected_book_id:
            messagebox.showerror("Error", "Selecciona un llibre abans d'editar.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE books
            SET title = ?, author = ?, genre = ?, available_qty = ?, library_id = ?, editorial_id = ?
            WHERE id = ?
            """,
            (
                book_data["title"],
                book_data["author"],
                book_data["genre"],
                book_data["available"],
                book_data["library"],
                book_data["editorial"],
                selected_book_id,
            ),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Editar Llibre", "Llibre editat correctament.")
        self.go_back()

    def go_back(self):
        self.controller.show_frame(ManageBooksFrame)
        self.controller.frames[ManageBooksFrame].refresh()


class DeleteBookFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Eliminar Llibre", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Títol", font=("Arial", 14)).pack()
        self.title_entry = tk.Entry(self, font=("Arial", 14))
        self.title_entry.pack()

        tk.Button(self, text="Eliminar", command=self.delete_book, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

    def delete_book(self):
        title = self.title_entry.get()

        if not title:
            messagebox.showerror("Error", "Especifica el títol del llibre a eliminar.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE title = ?", (title,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Eliminar Llibre", "Llibre eliminat correctament.")
        self.go_back()

    def go_back(self):
        self.controller.show_frame(ManageBooksFrame)
        self.controller.frames[ManageBooksFrame].refresh()


class AddBookFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Afegir Llibre", font=("Arial", 18)).pack(pady=20)

        self.fields = {
            "title": ("Títol", tk.Entry(self, font=("Arial", 14))),
            "author": ("Autor", tk.Entry(self, font=("Arial", 14))),
            "genre": ("Gènere", tk.Entry(self, font=("Arial", 14))),
            "available": ("Disponible", tk.Entry(self, font=("Arial", 14))),
            "library": ("Llibreria", ttk.Combobox(self, font=("Arial", 14))),
            "editorial": ("Editorial", ttk.Combobox(self, font=("Arial", 14))),
        }

        for field, (label, widget) in self.fields.items():
            tk.Label(self, text=label, font=("Arial", 14)).pack()
            widget.pack()

        tk.Button(self, text="Afegir", command=self.add_new_book, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack()

    def add_new_book(self):
        book_data = {field: widget.get() for field, (_, widget) in self.fields.items()}

        if not all(book_data.values()):
            messagebox.showerror("Error", "Tots els camps són obligatoris.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO books (title, author, genre, available_qty, library_id, editorial_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                book_data["title"],
                book_data["author"],
                book_data["genre"],
                book_data["available"],
                book_data["library"],
                book_data["editorial"],
            ),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Afegir Llibre", "Llibre afegit correctament.")
        self.go_back()

    def go_back(self):
        self.controller.show_frame(ManageBooksFrame)
        self.controller.frames[ManageBooksFrame].refresh()


# USER MODE
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


class ViewBookFrameUserMode(tk.Frame):
    def __init__(self, parent, controller, book_id=None):
        super().__init__(parent)
        self.controller = controller
        self.book_id = book_id

        tk.Label(self, text="Visualitzar Llibre", font=("Arial", 18)).pack(pady=20)
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(pady=10)

        tk.Button(self, text="Alquilar", command=self.rent_book, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Reservar", command=self.reserve_book, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

        self.refresh()

    def refresh(self, book_id=None):
        """Carga los detalles del libro seleccionado."""
        if book_id:
            self.book_id = book_id  # ✅ Guarda el ID del libro seleccionado

        if not self.book_id:
            messagebox.showerror("Error", "ID de libro no válido.")
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT b.id, b.title, b.author, COALESCE(g.name, 'Sense gènere') AS genre, 
                   COALESCE(e.name, 'Sense editorial') AS editorial, 
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

            labels = ["ID", "Títol", "Autor", "Gènere", "Editorial", "Quantitat disponible", "Reservats"]
            for i, value in enumerate(book):
                tk.Label(self.data_frame, text=f"{labels[i]}: {value}", font=("Arial", 14)).pack()
        else:
            messagebox.showerror("Error", "No s'ha trobat el llibre.")

    from datetime import datetime

    def rent_book(self):
        """Alquila un libro y lo registra en la base de datos."""
        if not self.book_id or not self.controller.current_user:
            messagebox.showerror("Error", "No s'ha trobat el llibre o l'usuari.")
            return

        user_id = self.controller.current_user[0]  # Obtener ID del usuario
        rent_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha actual

        conn = connect_db()
        cursor = conn.cursor()

        # Verificar si hay disponibilidad
        cursor.execute("SELECT available_qty FROM books WHERE id = %s", (self.book_id,))
        available_qty = cursor.fetchone()[0]

        if available_qty > 0:
            try:
                # Registrar el alquiler
                cursor.execute("UPDATE books SET available_qty = available_qty - 1 WHERE id = %s", (self.book_id,))
                cursor.execute("""
                    INSERT INTO rents (user_id, book_id, time_rented, status)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, self.book_id, rent_date, "rented"))

                # Confirmar la transacción
                conn.commit()
                messagebox.showinfo("Info", "Llibre llogat correctament.")
            except Exception as e:
                # Deshacer cambios si hay un error
                conn.rollback()
                messagebox.showerror("Error", f"Ha ocorregut un error: {str(e)}")
        else:
            messagebox.showerror("Error", "No hi ha llibres disponibles per alquilar.")

        conn.close()
        self.refresh()

    def reserve_book(self):
        """Reserva un libro y lo registra en la base de datos."""
        if not self.book_id or not self.controller.current_user:
            messagebox.showerror("Error", "No s'ha trobat el llibre o l'usuari.")
            return

        user_id = self.controller.current_user[0]
        reserve_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = connect_db()
        cursor = conn.cursor()

        # Verificar si hay disponibilidad
        cursor.execute("SELECT available_qty FROM books WHERE id = %s", (self.book_id,))
        available_qty = cursor.fetchone()[0]

        if available_qty > 0:
            messagebox.showwarning("Atenció", "El llibre està disponible, s'ha llogat automàticament.")
            self.rent_book()  # Llama a rent_book si el libro está disponible
        else:
            try:
                # Registrar la reserva (actualiza la cantidad de reservados)
                cursor.execute("UPDATE books SET reserved = reserved + 1 WHERE id = %s", (self.book_id,))

                # Registrar la inserción en la tabla de reservas
                cursor.execute("""
                    INSERT INTO reservations (book_id, user_id, time_reserved, status)
                    VALUES (%s, %s, %s, %s)
                """, (self.book_id, user_id, reserve_date, "reserved"))

                conn.commit()
                messagebox.showinfo("Info", "Llibre reservat correctament.")
            except Exception as e:
                # Deshacer cambios si hay un error
                conn.rollback()
                messagebox.showerror("Error", f"Ha ocorregut un error: {str(e)}")

        conn.close()
        self.refresh()

    def go_back(self):
        self.controller.show_frame(ListBooksUserMode)


class BookListBase(tk.Frame):
    def __init__(self, parent, controller, frame_title, table_columns, action_button_text, action_method):
        super().__init__(parent)
        self.controller = controller
        self.frame_title = frame_title
        self.table_columns = table_columns
        self.action_button_text = action_button_text
        self.action_method = action_method

        # Título
        tk.Label(self, text=self.frame_title, font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text=f"Llibres {frame_title.lower()}", font=("Arial", 14)).pack()

        # Contenedor para la tabla y scrollbar
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            container,
            columns=self.table_columns,
            show="headings",
        )
        for col in self.table_columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Botones
        tk.Button(self, text=self.action_button_text, command=self.action_method, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack(pady=10)

        self.refresh()

    def refresh(self):
        """Carga la lista de libros (alquilados o reservados) desde la base de datos."""
        self.tree.delete(*self.tree.get_children())

        conn = connect_db()
        cursor = conn.cursor()

        query = self.get_query()
        cursor.execute(query, (self.controller.current_user[0],))

        for book in cursor.fetchall():
            self.tree.insert("", "end", values=book)

        conn.close()

    def get_query(self):
        """Define la consulta SQL dependiendo de la clase."""
        raise NotImplementedError("Subclasses must implement this method.")

    def go_back(self):
        from classes.user_dashboard import UserDashboardFrame
        self.controller.show_frame(UserDashboardFrame)


class ListRentedBooks(BookListBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Llibres Llogats",
                         ("id", "title", "author", "genre", "editorial", "rented_date"),
                         "Retornar Llibre", self.return_book)

    def get_query(self):
        """Consulta SQL para obtener los libros alquilados por el usuario que no han sido devueltos o cuya renta no haya expirado."""
        return """
            SELECT b.id, b.title, b.author, g.name AS genre, e.name AS editorial, r.time_rented
            FROM rents r
            LEFT JOIN books b ON r.book_id = b.id
            LEFT JOIN books_genres bg ON b.id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.id
            LEFT JOIN editorial e ON b.editorial_id = e.id
            WHERE r.user_id = %s
            AND r.status = 'rented'
            AND NOT EXISTS (
                SELECT 1
                FROM returns re
                WHERE re.rent_id = r.id
            )
            AND DATEDIFF(CURDATE(), r.time_rented) <= 7  -- Solo alquilados por 7 días o menos
        """

    def return_book(self):
        """Devuelve un libro y actualiza la cantidad disponible."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenció", "Selecciona un llibre per retornar.")
            return

        book_id = self.tree.item(selected_item)["values"][0]
        user_id = self.controller.current_user[0]

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Obtener el rent_id del alquiler más reciente
            cursor.execute("""
                SELECT id
                FROM rents
                WHERE book_id = %s AND user_id = %s
                ORDER BY time_rented DESC
                LIMIT 1
            """, (book_id, user_id))
            rent_id = cursor.fetchone()

            if not rent_id:
                messagebox.showwarning("Atenció", "Aquest llibre no està llogat per tu.")
                conn.close()
                return

            rent_id = rent_id[0]

            # Verificar si el libro ya ha sido devuelto
            cursor.execute("""
                SELECT id
                FROM returns
                WHERE rent_id = %s
                LIMIT 1
            """, (rent_id,))
            existing_return = cursor.fetchone()

            if existing_return:
                messagebox.showwarning("Atenció", "Aquest llibre ja ha estat retornat.")
                conn.close()
                return

            # Insertar en la tabla 'returns'
            cursor.execute("""
                INSERT INTO returns (rent_id, time_returned) 
                VALUES (%s, %s)
            """, (rent_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            # Cambiar el estado de la renta a "returned"
            cursor.execute("""
                UPDATE rents
                SET status = 'returned'
                WHERE id = %s
            """, (rent_id,))

            # Actualizar la cantidad disponible de libros
            cursor.execute("""
                UPDATE books
                SET available_qty = available_qty + 1
                WHERE id = %s
            """, (book_id,))

            # Manejar la primera reserva
            cursor.execute("""
                SELECT user_id
                FROM reservations
                WHERE book_id = %s AND status = 'reserved'
                ORDER BY time_reserved ASC
                LIMIT 1
            """, (book_id,))
            first_reserver = cursor.fetchone()

            if first_reserver:
                first_reserver_id = first_reserver[0]

                # Cambiar la reserva de 'reserved' a 'rented' en lugar de 'cancelled'
                cursor.execute("""
                    UPDATE reservations
                    SET status = 'rented'
                    WHERE book_id = %s AND user_id = %s AND status = 'reserved'
                    LIMIT 1
                """, (book_id, first_reserver_id))

                # Insertar el alquiler para el primer usuario
                cursor.execute("""
                    INSERT INTO rents (user_id, book_id, time_rented, status)
                    VALUES (%s, %s, %s, 'rented')
                """, (first_reserver_id, book_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                # Actualizar la cantidad reservada del libro
                cursor.execute("""
                    UPDATE books
                    SET reserved = reserved - 1, available_qty = available_qty - 1
                    WHERE id = %s
                """, (book_id,))

            # Confirmar cambios
            conn.commit()
            messagebox.showinfo("Info", "Llibre retornat correctament.")
            self.refresh()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"S'ha produït un error: {e}")
        finally:
            conn.close()
            self.refresh()  # Actualiza la vista después de devolver el libro en cualquier caso


class ListReservedBooks(BookListBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Llibres Reservats",
                         ("id", "title", "author", "genre", "editorial", "reserved_date"),
                         "Cancelar Reserva", self.cancel_reservation)

    def get_query(self):
        """Consulta SQL para obtener los libros reservados por el usuario, excluyendo los ya alquilados."""
        return """
               SELECT b.id, b.title, b.author, g.name AS genre, e.name AS editorial, r.time_reserved
               FROM reservations r
               LEFT JOIN books b ON r.book_id = b.id
               LEFT JOIN books_genres bg ON b.id = bg.book_id
               LEFT JOIN genres g ON bg.genre_id = g.id
               LEFT JOIN editorial e ON b.editorial_id = e.id
               WHERE r.user_id = %s
               AND r.status = 'reserved'
           """

    def cancel_reservation(self):
        """Cancela la reserva de un libro y actualiza la cantidad reservada del libro."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenció", "Selecciona un llibre per cancel·lar la reserva.")
            return

        book_id = self.tree.item(selected_item)["values"][0]
        user_id = self.controller.current_user[0]

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Verificar si la reserva pertenece al usuario y no está ya alquilada
            cursor.execute("""
                SELECT id, status
                FROM reservations
                WHERE book_id = %s AND user_id = %s
                LIMIT 1
            """, (book_id, user_id))

            reservation = cursor.fetchone()

            if not reservation:
                messagebox.showwarning("Atenció", "Aquesta reserva no existeix o no és teva.")
                conn.close()
                return

            reservation_id, status = reservation

            if status == 'rented':
                messagebox.showwarning("Atenció", "Aquesta reserva ja ha estat llogada.")
                conn.close()
                return

            # Eliminar la reserva
            cursor.execute("""
                DELETE FROM reservations
                WHERE id = %s
            """, (reservation_id,))

            # Actualizar la cantidad de libros reservados
            cursor.execute("""
                UPDATE books
                SET reserved = reserved - 1
                WHERE id = %s
            """, (book_id,))

            # Verificar si hay una reserva pendiente para ese libro
            cursor.execute("""
                SELECT user_id
                FROM reservations
                WHERE book_id = %s AND status = 'reserved'
                ORDER BY time_reserved ASC
                LIMIT 1
            """, (book_id,))
            next_reserver = cursor.fetchone()

            if next_reserver:
                next_reserver_id = next_reserver[0]

                # Cancelar la siguiente reserva
                cursor.execute("""
                    UPDATE reservations
                    SET status = 'cancelled'
                    WHERE book_id = %s AND user_id = %s AND status = 'reserved'
                    LIMIT 1
                """, (book_id, next_reserver_id))

                # Insertar el nuevo alquiler para el siguiente usuario
                cursor.execute("""
                    INSERT INTO rents (user_id, book_id, time_rented, status)
                    VALUES (%s, %s, %s, 'rented')
                """, (next_reserver_id, book_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                # Actualizar la cantidad reservada del libro
                cursor.execute("""
                    UPDATE books
                    SET reserved = reserved - 1
                    WHERE id = %s
                """, (book_id,))

            # Confirmar cambios
            conn.commit()
            messagebox.showinfo("Info", "Reserva cancel·lada correctament.")
            self.refresh()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"S'ha produït un error: {e}")
        finally:
            conn.close()
