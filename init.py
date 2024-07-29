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
        # Abrir el archivo PDF
        documento = fitz.open(file_path)
        indice_encontrado = False
        for pagina_num, pagina in enumerate(documento):
            # Extraer texto completo de la página
            texto_pagina = pagina.get_text()
            
            # Filtrar el índice si está en las primeras páginas
            if pagina_num < 5:  # Asumir que el índice está en las primeras 5 páginas
                if not indice_encontrado:
                    indice_encontrado = es_indice(texto_pagina)
                    if indice_encontrado:
                        continue  # Saltar el índice

            # Filtrar pies de página
            texto_pagina = filtrar_pies_de_pagina(texto_pagina)
            texto += texto_pagina + "\n"  # Añadir un salto de línea entre páginas
        documento.close()
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        texto = None
    return texto

def es_indice(texto_pagina):
    # Heurística simple para detectar índice
    texto_pagina = texto_pagina.lower()
    return "índice" in texto_pagina or "tabla de contenidos" in texto_pagina or "contenido" in texto_pagina

def filtrar_pies_de_pagina(texto_pagina):
    # Filtrar líneas que probablemente sean pies de página
    lineas = texto_pagina.split('\n')
    lineas_filtradas = []

    # Asumir que las últimas líneas en cada página son pies de página
    for i in range(len(lineas) - 5):  # Ajusta el número de líneas a filtrar según sea necesario
        lineas_filtradas.append(lineas[i])

    return '\n'.join(lineas_filtradas)

def estimar_duracion(texto):
    # Estimar la duración del audio en minutos
    palabras_por_minuto = 150
    num_palabras = len(texto.split())
    duracion_minutos = num_palabras / palabras_por_minuto
    return round(duracion_minutos)

def texto_a_voz(texto, archivo_salida, progress_callback):
    try:
        # Crear el objeto gTTS con el texto y el idioma
        tts = gTTS(text=texto, lang='es', slow=False)
        
        # Simular progreso
        for i in range(10):
            time.sleep(0.1)  # Simular tiempo de procesamiento
            progress_callback(int((i + 1) / 10 * 100))
        
        # Guardar el archivo de salida
        tts.save(archivo_salida)
        print(f"Archivo de audio guardado como: {archivo_salida}")

        # Verificar que el archivo se ha creado
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
        
        # Detectar la extensión del archivo
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
        
        # Estimar la duración del audio y generar el nombre del archivo de salida
        duracion = estimar_duracion(texto)
        base_name = os.path.splitext(file_path)[0]
        archivo_salida = f"{base_name}_{duracion}min.mp3"
        
        # Reiniciar la barra de progreso
        update_progress(0)
        
        # Hilo para ejecutar la conversión sin bloquear la GUI
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

# Etiqueta para la interfaz
label = tk.Label(root, text='Arrastra y suelta un archivo de texto o PDF aquí', pady=20)
label.pack()

# Barra de progreso
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=20, padx=20, fill=tk.X)

# Configuración de arrastrar y soltar
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

# Ejecutar la aplicación
root.mainloop()
