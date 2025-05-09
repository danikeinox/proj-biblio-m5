import tkinter as tk
from tkinter import messagebox, ttk
from classes.database import connect_db


class EditUserFrame(tk.Frame):
    def __init__(self, parent, controller, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.controller = controller

        self.refresh(self.user_id)

    def refresh(self, user_id=None):
        self.user_id = user_id

        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Editar Usuari", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text="Nom", font=("Arial", 14)).pack()
        self.name_entry = tk.Entry(self, font=("Arial", 14))
        self.name_entry.pack()

        tk.Label(self, text="Usuari", font=("Arial", 14)).pack()
        self.username_entry = tk.Entry(self, font=("Arial", 14))
        self.username_entry.pack()

        self.is_admin = tk.BooleanVar()

        # 🟢 Bindings para eventos
        self.bind_all("<Double-1>", lambda e: None)
        self.bind_all("<Return>", lambda e: None)
        self.bind_all("<space>", lambda e: None)
        self.bind_all("<Delete>", lambda e: None)
        self.bind_all("<Escape>", lambda e: self.go_back())

        # Limpia eventos específicos del Treeview (si existe)
        if hasattr(self, "tree"):
            self.tree.unbind("<Double-1>")
            self.tree.unbind("<Return>")
            self.tree.unbind("<space>")
            self.tree.unbind("<Delete>")

        user = self.controller.get_user_by_id(self.user_id)

        self.name_entry.insert(0, user["name"])
        self.username_entry.insert(0, user["username"])
        self.is_admin = tk.BooleanVar(value=user["is_admin"])
        tk.Checkbutton(self, text="Administrador", variable=self.is_admin, font=("Arial", 14)).pack()

        tk.Button(self, text="Desar", command=self.save_user, font=("Arial", 14)).pack()
        tk.Button(self, text="Tornar", command=self.go_back, font=("Arial", 14)).pack()


    def save_user(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        is_admin = self.is_admin.get()
        user_id = self.user_id

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = %s, username = %s, is_admin = %s WHERE id = %s",
            (name, username, is_admin, user_id),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Èxit", "Usuari actualitzat correctament.")
        self.controller.frames[ManageUsersFrame].refresh_user_list()
        self.controller.show_frame(ManageUsersFrame)

    def go_back(self):
        from classes.user.ManageUsersFrame import ManageUsersFrame
        if hasattr(self.controller.frames[ManageUsersFrame], "refresh_user_list"):
            self.controller.frames[ManageUsersFrame].refresh_user_list()
        self.controller.show_frame(ManageUsersFrame)

