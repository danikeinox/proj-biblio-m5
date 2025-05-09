import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from datetime import datetime
from classes.books.User.BookListBase import BookListBase


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

            reservation_id = reservation[0]

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
