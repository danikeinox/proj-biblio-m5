import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from datetime import datetime
from classes.books.User.BookListBase import BookListBase


class ListRentedBooks(BookListBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Llibres Llogats",
                         ("id", "title", "author", "genre", "editorial", "rented_date"),
                         "Retornar Llibre", self.return_book)

    def get_query(self):
        """Consulta SQL para obtener los libros alquilados por el usuario que no han sido devueltos o cuya renta no
        haya expirado."""
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
