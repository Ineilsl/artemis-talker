import os
import threading
import time
import fitz  # PyMuPDF
from gtts import gTTS
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk

def extraer_texto_pdf(file_path):
    texto = ""
    try:
        documento = fitz.open(file_path)
        indice_encontrado = False
        for pagina_num, pagina in enumerate(documento):
            texto_pagina = pagina.get_text()
            if pagina_num < 5:
                if not indice_encontrado:
                    indice_encontrado = es_indice(texto_pagina)
                    if indice_encontrado:
                        continue
            texto_pagina = filtrar_encabezados_y_pies(texto_pagina)
            texto += texto_pagina + "\n"
        documento.close()
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        texto = None
    return texto

def es_indice(texto_pagina):
    texto_pagina = texto_pagina.lower()
    return "índice" in texto_pagina or "tabla de contenidos" in texto_pagina or "contenido" in texto_pagina

def filtrar_encabezados_y_pies(texto_pagina):
    lineas = texto_pagina.split('\n')
    if len(lineas) < 2:
        return texto_pagina

    # Intentar detectar y filtrar encabezados y pies de página
    lineas_filtradas = []

    # Suponer que los encabezados y pies de página están en las primeras y últimas 2 líneas
    for i in range(2, len(lineas) - 2):
        lineas_filtradas.append(lineas[i])

    return '\n'.join(lineas_filtradas)

def texto_a_voz(texto, archivo_salida, progress_callback):
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        for i in range(10):
            time.sleep(0.1)
            progress_callback(int((i + 1) / 10 * 100))
        tts.save(archivo_salida)
        print(f"Archivo de audio guardado como: {archivo_salida}")
        if os.path.exists(archivo_salida):
            root.after(0, lambda: messagebox.showinfo("Completado", "La conversión de texto a voz se ha completado y el archivo se ha guardado."))
        else:
            root.after(0, lambda: messagebox.showerror("Error", "No se pudo guardar el archivo de audio."))
    except Exception as e:
        print(f"Error: {e}")
        root.after(0, lambda: messagebox.showerror("Error", f"Se produjo un error: {e}"))

def drop(event):
    try:
        file_path = event.data.strip('{}')
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            texto = extraer_texto_pdf(file_path)
        elif ext in ['.txt', '.text']:
            with open(file_path, 'r', encoding='utf-8') as file:
                texto = file.read()
        else:
            messagebox.showerror("Error", "Solo se admiten archivos de texto (.txt) y PDF (.pdf).")
            return
        if texto is None or texto.strip() == "":
            messagebox.showerror("Error", "No se pudo extraer texto del archivo.")
            return
        base_name = os.path.splitext(file_path)[0]
        archivo_salida = f"{base_name}.mp3"
        update_progress(0)
        threading.Thread(target=texto_a_voz, args=(texto, archivo_salida, update_progress)).start()
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        messagebox.showerror("Error", f"Se produjo un error al procesar el archivo: {e}")

def update_progress(value):
    progress_var.set(value)

# Configuración de la ventana
root = TkinterDnD.Tk()
root.title('Arrastra y suelta un archivo de texto o PDF aquí')
root.geometry('400x200')

label = tk.Label(root, text='Arrastra y suelta un archivo de texto o PDF aquí', pady=20)
label.pack()

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=20, padx=20, fill=tk.X)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

root.mainloop()
