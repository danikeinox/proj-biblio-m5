import tkinter as tk
from tkinter import ttk, messagebox
from classes.database import connect_db
from datetime import datetime

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

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

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
