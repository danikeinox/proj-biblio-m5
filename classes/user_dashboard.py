import tkinter as tk


class UserDashboardFrame(tk.Frame):
    def __init__(self, parent, controller, name):
        super().__init__(parent)
        self.name = name
        self.controller = controller

        tk.Label(self, text=f"Benvingut usuari: {name}", font=("Arial", 18)).pack(pady=20)
        tk.Button(self, text="Alquilar Llibres", command=self.rent_book, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Veure Llibres Alquilats", command=self.manage_rent_books, font=("Arial", 14)).pack(
            pady=10)
        tk.Button(self, text="Veure Llibres Reservats", command=self.manage_reserved_books, font=("Arial", 14)).pack(
            pady=10)
        tk.Button(self, text="Tancar Sessió", command=self.controller.logout, font=("Arial", 14)).pack(pady=10)

    def refresh_user_data(self):
        if not self.controller.current_user:
            messagebox.showerror("Error", "Sessió no iniciada. Torna a iniciar sessió.")
            self.go_to_login()
            return
        self.name = self.controller.current_user[1]
        for widget in self.winfo_children():
            widget.destroy()
        tk.Label(self, text=f"Benvingut usuari: {self.name}", font=("Arial", 18)).pack(pady=20)
        tk.Button(self, text="Alquilar Llibres", command=self.rent_book, font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Veure Llibres Alquilats", command=self.manage_rent_books, font=("Arial", 14)).pack(
            pady=10)
        tk.Button(self, text="Veure Llibres Reservats", command=self.manage_reserved_books, font=("Arial", 14)).pack(
            pady=10)
        tk.Button(self, text="Tancar Sessió", command=self.controller.logout, font=("Arial", 14)).pack(pady=10)

    def rent_book(self):
        from classes.books import ListBooksUserMode
        self.controller.show_frame(ListBooksUserMode)

    def manage_rent_books(self):
        from classes.books import ListRentedBooks
        self.controller.show_frame(ListRentedBooks)

    def manage_reserved_books(self):
        from classes.books import ListReservedBooks
        self.controller.show_frame(ListReservedBooks)
