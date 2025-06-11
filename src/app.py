import tkinter as tk
from tkinter import messagebox, simpledialog

import db
from fingerprint import FingerprintSensor


def ensure_db():
    db.init_db()


def prompt_name(default=""):
    return simpledialog.askstring("Nombre", "Nombre del usuario", initialvalue=default)


def prompt_role(default="trabajador"):
    return simpledialog.askstring("Rol", "Rol (trabajador/administrador)", initialvalue=default)


class App:
    def __init__(self, root):
        self.root = root
        self.sensor = FingerprintSensor()
        ensure_db()
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20)
        self.show_scan()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_scan(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Escanee su huella").pack(pady=10)
        tk.Button(self.main_frame, text="Simular", command=self.handle_scan).pack()

    def handle_scan(self):
        user_id = self.sensor.scan_fingerprint()
        if user_id is None:
            messagebox.showerror("Error", "No se reconoció la huella")
            return
        user = db.get_user(user_id)
        if not user or not user[3]:
            messagebox.showerror("Error", "Usuario no válido o inactivo")
            return
        role = user[2]
        if role == 'administrador':
            self.show_admin_menu(user)
        else:
            self.show_worker_menu(user)

    def show_worker_menu(self, user):
        self.clear_frame()
        tk.Label(self.main_frame, text=f"Bienvenido {user[1]}").pack(pady=10)
        tk.Button(self.main_frame, text="Entrada", command=lambda: self.register_event(user[0], 'entrada')).pack(fill='x')
        tk.Button(self.main_frame, text="Salida", command=lambda: self.register_event(user[0], 'salida')).pack(fill='x')
        tk.Button(self.main_frame, text="Descanso", command=lambda: self.show_break_menu(user)).pack(fill='x')
        tk.Button(self.main_frame, text="Cerrar", command=self.show_scan).pack(pady=10)

    def show_break_menu(self, user):
        self.clear_frame()
        tk.Label(self.main_frame, text="Tipo de descanso").pack(pady=10)
        for tipo in ['cafe', 'comida', 'otro']:
            tk.Button(self.main_frame, text=tipo.capitalize(), command=lambda t=tipo: self.register_event(user[0], f'descanso_{t}')).pack(fill='x')
        tk.Button(self.main_frame, text="Volver", command=lambda: self.show_worker_menu(user)).pack(pady=10)

    def register_event(self, user_id, event):
        db.log_event(user_id, event)
        messagebox.showinfo("Registrado", f"Evento {event} registrado")
        self.show_scan()

    # Admin menu
    def show_admin_menu(self, user):
        self.clear_frame()
        tk.Label(self.main_frame, text=f"Admin {user[1]}").pack(pady=10)
        tk.Button(self.main_frame, text="Crear usuario", command=self.admin_create_user).pack(fill='x')
        tk.Button(self.main_frame, text="Modificar usuario", command=self.admin_modify_user).pack(fill='x')
        tk.Button(self.main_frame, text="Baja usuario", command=self.admin_deactivate_user).pack(fill='x')
        tk.Button(self.main_frame, text="Reactivar usuario", command=self.admin_reactivate_user).pack(fill='x')
        tk.Button(self.main_frame, text="Ver fichajes", command=self.admin_view_records).pack(fill='x')
        tk.Button(self.main_frame, text="Exportar CSV", command=self.export_csv).pack(fill='x')
        tk.Button(self.main_frame, text="Cerrar", command=self.show_scan).pack(pady=10)

    def admin_create_user(self):
        name = prompt_name()
        if not name:
            return
        role = prompt_role()
        user_id = db.add_user(name, role)
        sensor_id = self.sensor.enroll_user(user_id)
        db.update_user(user_id, sensor_id=sensor_id)
        messagebox.showinfo("OK", f"Usuario {name} creado con id {user_id}")

    def admin_modify_user(self):
        try:
            user_id = int(simpledialog.askstring("ID", "ID de usuario"))
        except (TypeError, ValueError):
            return
        user = db.get_user(user_id)
        if not user:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        new_name = prompt_name(user[1])
        new_role = prompt_role(user[2])
        db.update_user(user_id, name=new_name, role=new_role)
        messagebox.showinfo("Modificado", "Usuario actualizado")

    def admin_deactivate_user(self):
        try:
            user_id = int(simpledialog.askstring("ID", "ID de usuario"))
        except (TypeError, ValueError):
            return
        user = db.get_user(user_id)
        if not user:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        if user[4]:
            self.sensor.delete_fingerprint(user[4])
        db.update_user(user_id, active=0, sensor_id=None)
        messagebox.showinfo("Baja", "Usuario desactivado")

    def admin_reactivate_user(self):
        try:
            user_id = int(simpledialog.askstring("ID", "ID de usuario"))
        except (TypeError, ValueError):
            return
        user = db.get_user(user_id)
        if not user:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        sensor_id = self.sensor.enroll_user(user_id)
        db.update_user(user_id, active=1, sensor_id=sensor_id)
        messagebox.showinfo("Reactivado", "Usuario reactivado")

    def admin_view_records(self):
        records = db.list_records()
        self.clear_frame()
        tk.Label(self.main_frame, text="Fichajes").pack(pady=5)
        text = tk.Text(self.main_frame, width=40, height=10)
        text.pack()
        for r in records:
            text.insert('end', f"{r[1]} - {r[2]} - {r[3]}\n")
        tk.Button(self.main_frame, text="Volver", command=lambda: self.show_admin_menu(db.get_user(records[0][0]) if records else None)).pack(pady=10)

    def export_csv(self):
        import csv
        records = db.list_records()
        with open('fichajes.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'usuario', 'evento', 'fecha'])
            for r in records:
                writer.writerow(r)
        messagebox.showinfo("Exportado", "Datos exportados a fichajes.csv")


def main():
    root = tk.Tk()
    root.title("Fichaje por huella")
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
