import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from cryptography.fernet import Fernet
import hashlib
import base64

# ==========================================
# CONFIGURACIÓN
# ==========================================

ADMIN_PASSWORD = "admin123"  # 🔐 Cambiar aquí
WORKERS_FOLDER = "trabajadores"

# 🔐 Clave maestra interna del sistema (NO CAMBIAR)
MASTER_KEY = base64.urlsafe_b64encode(hashlib.sha256(b"SistemaFichajeUltraSeguro2026").digest())
cipher = Fernet(MASTER_KEY)

if not os.path.exists(WORKERS_FOLDER):
    os.makedirs(WORKERS_FOLDER)


# ==========================================
# FUNCIONES SEGURAS
# ==========================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def encrypt_data(data_dict):
    json_data = json.dumps(data_dict).encode()
    return cipher.encrypt(json_data)


def decrypt_data(encrypted_data):
    decrypted = cipher.decrypt(encrypted_data)
    return json.loads(decrypted.decode())


# ==========================================
# APP
# ==========================================

class TimeClockApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Fichaje Seguro")
        self.root.geometry("900x500")

        self.workers = {}
        self.selected_worker = None

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        self.create_widgets()
        self.load_workers()

    # ==========================================
    # INTERFAZ
    # ==========================================

    def create_widgets(self):

        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.worker_listbox = tk.Listbox(self.left_frame, font=("Arial", 14))
        self.worker_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.worker_listbox.bind("<<ListboxSelect>>", self.select_worker)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        for i in range(3):
            self.right_frame.rowconfigure(i, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        self.clock_button = tk.Button(
            self.right_frame,
            text="FICHAR",
            bg="green",
            fg="white",
            font=("Arial", 20),
            command=self.clock_action
        )
        self.clock_button.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        self.add_button = tk.Button(
            self.right_frame,
            text="Agregar Trabajador",
            bg="#ffcc80",
            font=("Arial", 14),
            command=self.add_worker
        )
        self.add_button.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.delete_button = tk.Button(
            self.right_frame,
            text="Eliminar Trabajador",
            bg="#ff9999",
            font=("Arial", 14),
            command=self.delete_worker
        )
        self.delete_button.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    # ==========================================
    # CARGAR TRABAJADORES
    # ==========================================

    def load_workers(self):
        self.worker_listbox.delete(0, tk.END)
        self.workers.clear()

        for file in os.listdir(WORKERS_FOLDER):
            if file.endswith(".dat"):
                name = file.replace(".dat", "")
                self.workers[name] = {"working": False, "start_time": None}
                self.worker_listbox.insert(tk.END, name)

    # ==========================================
    # SELECCIÓN
    # ==========================================

    def select_worker(self, event):
        selection = self.worker_listbox.curselection()
        if selection:
            self.selected_worker = self.worker_listbox.get(selection[0])
            self.update_button()

    def update_button(self):
        if not self.selected_worker:
            return

        worker = self.workers[self.selected_worker]

        if worker["working"]:
            self.clock_button.config(text="FINALIZAR", bg="red")
        else:
            self.clock_button.config(text="FICHAR", bg="green")

    # ==========================================
    # FICHAR
    # ==========================================

    def clock_action(self):

        if not self.selected_worker:
            messagebox.showwarning("Aviso", "Selecciona un trabajador")
            return

        password = simpledialog.askstring("Contraseña", "Introduce contraseña:", show="*")
        if not password:
            return

        file_path = os.path.join(WORKERS_FOLDER, f"{self.selected_worker}.dat")

        with open(file_path, "rb") as f:
            data = decrypt_data(f.read())

        # 🔐 VALIDACIÓN REAL
        if data["password_hash"] != hash_password(password):
            messagebox.showerror("Error", "Contraseña incorrecta")
            return

        worker = self.workers[self.selected_worker]

        if not worker["working"]:
            worker["working"] = True
            worker["start_time"] = datetime.now()
            self.worker_listbox.itemconfig(
                self.worker_listbox.curselection(),
                bg="orange"
            )
            self.update_button()
        else:
            end_time = datetime.now()
            start_time = worker["start_time"]

            data["registros"].append({
                "fecha": start_time.strftime("%d/%m/%Y"),
                "inicio": start_time.strftime("%H:%M:%S"),
                "fin": end_time.strftime("%H:%M:%S")
            })

            with open(file_path, "wb") as f:
                f.write(encrypt_data(data))

            worker["working"] = False
            worker["start_time"] = None

            self.worker_listbox.itemconfig(
                self.worker_listbox.curselection(),
                bg="white"
            )

            self.update_button()

    # ==========================================
    # AGREGAR
    # ==========================================

    def add_worker(self):

        admin_pass = simpledialog.askstring("Admin", "Contraseña administrador:", show="*")
        if admin_pass != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Contraseña incorrecta")
            return

        name = simpledialog.askstring("Nombre", "Nombre del trabajador:")
        if not name:
            return

        password = simpledialog.askstring("Contraseña", "Contraseña del trabajador:", show="*")
        if not password:
            return

        file_path = os.path.join(WORKERS_FOLDER, f"{name}.dat")

        if os.path.exists(file_path):
            messagebox.showerror("Error", "Ya existe")
            return

        data = {
            "password_hash": hash_password(password),
            "registros": []
        }

        with open(file_path, "wb") as f:
            f.write(encrypt_data(data))

        self.load_workers()

    # ==========================================
    # ELIMINAR
    # ==========================================

    def delete_worker(self):

        if not self.selected_worker:
            return

        confirm = messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar?")
        if not confirm:
            return

        admin_pass = simpledialog.askstring("Admin", "Contraseña administrador:", show="*")
        if admin_pass != ADMIN_PASSWORD:
            messagebox.showerror("Error", "Contraseña incorrecta")
            return

        file_path = os.path.join(WORKERS_FOLDER, f"{self.selected_worker}.dat")
        os.remove(file_path)
        self.load_workers()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeClockApp(root)
    root.mainloop()