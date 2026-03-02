import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from cryptography.fernet import Fernet
import hashlib
import base64
import json

ADMIN_PASSWORD = "admin123"

MASTER_KEY = base64.urlsafe_b64encode(hashlib.sha256(b"SistemaFichajeUltraSeguro2026").digest())
cipher = Fernet(MASTER_KEY)


def decrypt_file():

    admin_pass = simpledialog.askstring("Admin", "Contraseña administrador:", show="*")
    if admin_pass != ADMIN_PASSWORD:
        messagebox.showerror("Error", "Contraseña incorrecta")
        return

    file_path = filedialog.askopenfilename(filetypes=[("Archivos DAT", "*.dat")])
    if not file_path:
        return

    try:
        with open(file_path, "rb") as f:
            data = json.loads(cipher.decrypt(f.read()).decode())

        text_output = ""

        for r in data["registros"]:
            text_output += (
                f"Fecha: {r['fecha']}\n"
                f"Inicio: {r['inicio']}\n"
                f"Fin: {r['fin']}\n"
                f"----------------------\n"
            )

        result = tk.Toplevel(root)
        result.title("Registros")

        text = tk.Text(result, width=80, height=30)
        text.pack()
        text.insert(tk.END, text_output)

    except:
        messagebox.showerror("Error", "Archivo inválido")


root = tk.Tk()
root.title("Desencriptador Seguro")
root.geometry("400x200")

btn = tk.Button(root, text="Desencriptar archivo",
                font=("Arial", 14),
                command=decrypt_file)
btn.pack(expand=True)

root.mainloop()