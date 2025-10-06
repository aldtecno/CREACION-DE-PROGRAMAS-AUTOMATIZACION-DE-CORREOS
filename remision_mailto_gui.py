"""Aplicación GUI para generar un correo de remisión vía mailto."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox
from urllib.parse import quote
import webbrowser

# ---------------------------------------------------------------------------
# Configuración editable
# ---------------------------------------------------------------------------
# Lista de correos disponibles como destinatarios.  Puede agregar, quitar o
# cambiar elementos según lo requiera la institución.
AVAILABLE_RECIPIENTS = [
    "referenciaycontrarreferencia2@hospitalpitalito.gov.co",
    "referenciaycontrarreferencia@clinicareinaisabel.com",
]

# Texto base del asunto.  El nombre del paciente se añadirá automáticamente al
# final para completar la frase.
SUBJECT_TEMPLATE = (
    "Solicitud de aceptación de paciente en segundo nivel de complejidad – "
    "{nombre_paciente}"
)

# Texto del cuerpo del mensaje.  Las llaves {campo} serán reemplazadas por la
# información ingresada en el formulario.
BODY_TEMPLATE = """Estimados,\n\n""" \
    "Por medio de la presente me permito solicitar la aceptación del paciente " \
    "{nombre_paciente},\n" \
    "identificado con documento {documento_identidad}, de {edad} años,\n" \
    "para la especialidad de {especialidad}.\n\n" \
    "Agradezco de antemano su colaboración y quedo atento a su confirmación.\n\n" \
    "Atentamente,\n" \
    "{nombre_remitente}\n" \
    "{cargo_remitente}\n" \
    "TELEFONO: 3138899808\n" \
    "CORREO: urgenciasaladoblanco@yahoo.com.co"

# Posibles ubicaciones del ejecutable de Google Chrome en Windows.  Ajuste la
# ruta si Chrome está instalado en una carpeta diferente.
CHROME_PATHS = [
    r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
]

# ---------------------------------------------------------------------------
# Funciones de utilidad
# ---------------------------------------------------------------------------

def build_mailto_link(destinations: list[str], subject: str, body: str) -> str:
    """Construye y codifica un enlace mailto listo para abrir en el navegador."""
    if not destinations:
        raise ValueError("Debe seleccionar al menos un destinatario")

    to_field = quote(",".join(destinations))
    subject_field = quote(subject)
    body_field = quote(body)
    return f"mailto:{to_field}?subject={subject_field}&body={body_field}"


def open_in_chrome(url: str) -> None:
    """Abre un enlace en Google Chrome, o en el navegador por defecto si no se encuentra."""
    for path in CHROME_PATHS:
        if os.path.isfile(path):
            webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(path))
            webbrowser.get("chrome").open(url)
            return

    # Si Chrome no está en las rutas previstas, recurrimos al navegador predeterminado.
    webbrowser.open(url)


# ---------------------------------------------------------------------------
# Interfaz gráfica
# ---------------------------------------------------------------------------

def main() -> None:
    """Crea y ejecuta la ventana del formulario."""
    root = tk.Tk()
    root.title("Solicitud de remisión a segundo nivel")

    # Crea la grilla principal con márgenes.
    container = tk.Frame(root, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    # Etiquetas y campos de entrada de texto.
    labels = [
        ("Nombre completo del paciente", "nombre_paciente"),
        ("Documento de identidad", "documento_identidad"),
        ("Edad", "edad"),
        ("Especialidad", "especialidad"),
        ("Nombre del remitente", "nombre_remitente"),
        ("Cargo del remitente", "cargo_remitente"),
    ]

    entries: dict[str, tk.Entry] = {}
    for row, (label_text, key) in enumerate(labels):
        tk.Label(container, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=5)
        entry = tk.Entry(container, width=50)
        entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        entries[key] = entry

    # Sección de selección de destinatarios mediante checkboxes.
    tk.Label(container, text="Enviar correo a:").grid(row=len(labels), column=0, sticky=tk.W, pady=(15, 5))
    recipient_vars: list[tk.BooleanVar] = []
    for idx, recipient in enumerate(AVAILABLE_RECIPIENTS):
        var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(container, text=recipient, variable=var)
        chk.grid(row=len(labels) + idx, column=1, sticky=tk.W)
        recipient_vars.append(var)

    def send_request() -> None:
        """Genera el enlace mailto y lo abre en el navegador."""
        values = {key: entry.get().strip() for key, entry in entries.items()}

        # Validaciones básicas.
        missing_fields = [label for label, key in labels if not values[key]]
        if missing_fields:
            messagebox.showwarning(
                "Campos incompletos",
                "Debe completar todos los campos antes de enviar la solicitud.",
            )
            return

        if not values["edad"].isdigit():
            messagebox.showwarning("Edad inválida", "La edad debe contener solo números.")
            return

        selected_recipients = [recipient for recipient, var in zip(AVAILABLE_RECIPIENTS, recipient_vars) if var.get()]
        if not selected_recipients:
            messagebox.showwarning(
                "Sin destinatario",
                "Seleccione al menos un correo electrónico de destino.",
            )
            return

        subject = SUBJECT_TEMPLATE.format(nombre_paciente=values["nombre_paciente"])
        body = BODY_TEMPLATE.format(**values)

        try:
            mailto_link = build_mailto_link(selected_recipients, subject, body)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        open_in_chrome(mailto_link)
        messagebox.showinfo(
            "Correo listo",
            "Se ha abierto Google Chrome con el correo listo para enviar en Yahoo Mail.",
        )

    send_button = tk.Button(container, text="Enviar Solicitud", command=send_request)
    send_button.grid(row=len(labels) + len(AVAILABLE_RECIPIENTS), column=0, columnspan=2, pady=(20, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
