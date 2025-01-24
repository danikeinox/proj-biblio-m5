import tkinter as tk
from classes.login import LoginFrame
from classes.register import RegisterFrame
from classes.user import ViewUserFrame, ManageUsersFrame
from classes.database import connect_db
from datetime import datetime, timedelta


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Llibreries de Daniel")
        self.geometry("800x600")
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}  # Diccionario para gestionar frames
        self.current_user = None  # Variable para almacenar el usuario actual
        self.connection_error = False  # Inicializa la bandera de error de conexión
        self.show_frame(LoginFrame)

        # Llamada a la función para iniciar la comprobación periódica y al iniciar la aplicación
        self.check_rentals_and_reservations()

    def check_rentals_and_reservations(self):
        """Verifica y actualiza reservas y alquileres cada minuto."""
        conn = connect_db()
        cursor = conn.cursor()

        # 🟢 1. Verificar alquileres vencidos (más de 7 días)
        cursor.execute("""
            SELECT id, book_id, user_id
            FROM rents
            WHERE status = 'rented' AND DATEDIFF(CURDATE(), time_rented) > 7
        """)
        returned_rentals = cursor.fetchall()

        for rental_id, book_id, user_id in returned_rentals:
            cursor.execute("UPDATE rents SET status = 'returned' WHERE id = %s", (rental_id,))
            cursor.execute("UPDATE books SET available_qty = available_qty + 1 WHERE id = %s", (book_id,))

            # 🟢 2. Buscar la primera reserva para este libro
            cursor.execute("""
                SELECT user_id FROM reservations
                WHERE book_id = %s AND status = 'reserved'
                ORDER BY time_reserved ASC LIMIT 1
            """, (book_id,))
            first_reserver = cursor.fetchone()

            if first_reserver:
                first_reserver_id = first_reserver[0]

                # Verificar si el usuario ya tiene este libro alquilado
                cursor.execute("""
                    SELECT id FROM rents WHERE user_id = %s AND book_id = %s AND status = 'rented'
                """, (first_reserver_id, book_id))
                existing_rent = cursor.fetchone()

                if not existing_rent:  # Solo crear el alquiler si no existe
                    cursor.execute("""
                        UPDATE reservations SET status = 'notified'
                        WHERE book_id = %s AND user_id = %s LIMIT 1
                    """, (book_id, first_reserver_id))

                    cursor.execute("""
                        INSERT INTO rents (user_id, book_id, time_rented, status)
                        VALUES (%s, %s, %s, 'rented')
                    """, (first_reserver_id, book_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                    cursor.execute("""
                        UPDATE books SET reserved = reserved - 1, available_qty = available_qty - 1 WHERE id = %s
                    """, (book_id,))

        conn.commit()
        conn.close()
        self.after(60000, self.check_rentals_and_reservations)

    def check_and_notify_user_reservations(self, user_id):
        """Verifica si el usuario tiene reservas convertidas en alquiler y envía notificación."""
        if not user_id:
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.book_id, b.title
            FROM reservations r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = %s AND r.status = 'notified'
        """, (user_id,))
        reservations = cursor.fetchall()

        for book_id, book_name in reservations:
            # 🟢 Verificar si ya existe un alquiler activo
            cursor.execute("""
                SELECT id FROM rents WHERE user_id = %s AND book_id = %s AND status = 'rented'
            """, (user_id, book_id))
            existing_rent = cursor.fetchone()

            if existing_rent:
                # ✅ Si el usuario ya tiene el libro alquilado, cancelar la reserva
                cursor.execute("""
                    UPDATE reservations SET status = 'cancelled' 
                    WHERE book_id = %s AND user_id = %s
                """, (book_id, user_id))

                message = f"La reserva del llibre '{book_name}' ha estat cancel·lada perquè ja el tens llogat."
                self.show_notification(message, book_id, user_id)

            else:
                # ✅ Si el usuario no tiene el libro alquilado, convertir la reserva en alquiler
                cursor.execute("""
                    UPDATE reservations SET status = 'rented' 
                    WHERE book_id = %s AND user_id = %s
                """, (book_id, user_id))

                cursor.execute("""
                    INSERT INTO rents (user_id, book_id, time_rented, status)
                    VALUES (%s, %s, %s, 'rented')
                """, (user_id, book_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                rental_end_date = datetime.now() + timedelta(days=7)

                cursor.execute("SELECT rented_notification_seen FROM users WHERE id = %s", (user_id,))
                rented_notification_seen = cursor.fetchone()[0]

                if not rented_notification_seen:
                    message = f"El llibre '{book_name}' que has reservat ha sigut alquilat fins el {rental_end_date.strftime('%d/%m/%Y')}."
                    self.show_notification(message, book_id, user_id)
                    cursor.execute("UPDATE users SET rented_notification_seen = TRUE WHERE id = %s", (user_id,))

        conn.commit()
        conn.close()

    def show_notification(self, message, book_id=None, user_id=None):
        """Muestra una notificación al usuario."""
        notification_window = tk.Toplevel(self)
        notification_window.title("Notificación")

        tk.Label(notification_window, text=message, padx=20, pady=20).pack()

        def close_notification():
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE reservations SET status = 'cancelled' 
                WHERE book_id = %s AND user_id = %s AND status = 'notified'
            """, (book_id, user_id))

            cursor.execute("UPDATE users SET rented_notification_seen = FALSE WHERE id = %s", (user_id,))
            conn.commit()
            conn.close()

            notification_window.destroy()

        tk.Button(notification_window, text="Cerrar", command=close_notification).pack(pady=10)

    def logout(self):
        """Cierra sesión y vuelve al LoginFrame, asegurando que el usuario anterior no queda almacenado."""
        # 🟢 Limpia la ventana actual
        for frame in self.frames.values():
            frame.pack_forget()
        self.current_user = None  # 🟢 Restablece el usuario actual
        self.frames = {}  # 🟢 Elimina todos los frames almacenados para evitar datos en caché

        self.show_frame(LoginFrame)  # 🟢 Vuelve a la pantalla de login
    @staticmethod
    def get_user_by_id(user_id):
        """Devuelve la información del usuario desde la base de datos."""
        conn = connect_db()
        cursor = conn.cursor()

        # Busca el usuario por id
        cursor.execute("SELECT id, name, username, is_admin FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "id": result[0],
                "name": result[1],
                "username": result[2],
                "is_admin": bool(result[3]),
            }
        else:
            return None

    @staticmethod
    def get_editorial_by_id(editorial_id):
        """Devuelve la información de la editorial desde la base de datos."""
        conn = connect_db()
        cursor = conn.cursor()

        # Busca editorial por id
        cursor.execute(
            "SELECT id, name, address, phone, username, website, country, city, postal_code FROM editorial WHERE id = %s",
            (editorial_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "id": result[0],
                "name": result[1],
                "address": result[2],
                "phone": result[3],
                "username": result[4],
                "website": result[5],
                "country": result[6],
                "city": result[7],
                "postal_code": result[8],
            }
        else:
            return None

    @staticmethod
    def get_rent_books(user_id):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM rents WHERE user_id = %s", (user_id,))
        result = cursor.fetchall()
        conn.close()

        return result

    @staticmethod
    def get_user_reservations(user_id):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
        result = cursor.fetchall()
        conn.close()

        return result

    def show_frame(self, frame_class, *args):
        """Muestra un frame específico."""
        # Destruye el frame actual
        for frame in self.frames.values():
            frame.pack_forget()

        if frame_class not in self.frames:
            # Crea el frame si no existe
            frame = frame_class(self.container, self, *args)
            self.frames[frame_class] = frame
            frame.pack(fill="both", expand=True)
        else:
            # Si ya existe, lo muestra
            self.frames[frame_class].pack(fill="both", expand=True)

        # Si se está accediendo a ViewUserFrame con un user_id, se crea un nuevo frame
        if frame_class == ViewUserFrame and args:
            if frame_class in self.frames:
                self.frames[frame_class].destroy()  # Eliminar el frame anterior
            frame = frame_class(self.container, self, *args)
            self.frames[frame_class] = frame
        elif frame_class not in self.frames:
            frame = frame_class(self.container, self, *args)
            self.frames[frame_class] = frame
        else:
            frame = self.frames[frame_class]

        frame.pack(fill="both", expand=True)
        frame.tkraise()

        # Llama a un método de actualización si el frame lo tiene
        if hasattr(self.frames[frame_class], "refresh"):
            self.frames[frame_class].refresh(*args)

        # Si se vuelve a ManageUsersFrame, asegurarse de que se actualice la lista
        if frame_class == ManageUsersFrame:
            frame.refresh_user_list()

        frame = self.frames[frame_class]
        if hasattr(frame, "refresh_user_data"):
            frame.refresh_user_data()

        if hasattr(frame, "refresh_editorial_data"):
            frame.refresh_editorial_data()
        frame.tkraise()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
