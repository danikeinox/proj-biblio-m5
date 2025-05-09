import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db


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

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

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
        from classes.books.Admin.ManageBooksFrame import ManageBooksFrame
        self.controller.show_frame(ManageBooksFrame)
        self.controller.frames[ManageBooksFrame].refresh()
