import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from datetime import datetime


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

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

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

            labels = ["ID", "Títol", "Autor", "Gènere", "Editorial", "Stock disponible", "Reservats"]
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

        # Verificar si el usuario ya tiene el libro alquilado
        cursor.execute("""
            SELECT id
            FROM rents
            WHERE book_id = %s AND user_id = %s AND status = 'rented'
        """, (self.book_id, user_id))
        existing_rent = cursor.fetchone()

        if existing_rent:
            messagebox.showwarning("Atenció", "Ja tens aquest llibre llogat.")
            conn.close()
            return

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

        # Verificar si el usuario ya tiene el libro alquilado
        cursor.execute("""
            SELECT id
            FROM rents
            WHERE book_id = %s AND user_id = %s AND status = 'rented'
        """, (self.book_id, user_id))
        existing_rent = cursor.fetchone()

        if existing_rent:
            messagebox.showwarning("Atenció", "Ja tens aquest llibre llogat, no pots reservar-lo.")
            conn.close()
            return

        # Verificar si el usuario ya tiene una reserva activa para este libro
        cursor.execute("""
            SELECT id
            FROM reservations
            WHERE book_id = %s AND user_id = %s AND status = 'reserved'
        """, (self.book_id, user_id))
        existing_reservation = cursor.fetchone()

        if existing_reservation:
            messagebox.showwarning("Atenció", "Ja has reservat aquest llibre.")
            conn.close()
            return

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
        from classes.books.User.ListBooksUserMode import ListBooksUserMode
        self.controller.show_frame(ListBooksUserMode)
