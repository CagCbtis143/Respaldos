import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import shutil
from datetime import datetime
import json
import logging
from PIL import Image, ImageTk

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Funciones Auxiliares de Perfiles ---
def guardar_perfiles(perfiles):
    """Guarda la lista de perfiles en un archivo JSON."""
    try:
        with open('perfiles.json', 'w') as f:
            json.dump(perfiles, f, indent=4)
    except IOError as e:
        messagebox.showerror("Error de Guardado", f"No se pudo guardar el archivo de perfiles: {e}")

def cargar_perfiles():
    """Carga los perfiles desde un archivo JSON. Si no existe, devuelve una lista vacía."""
    if os.path.exists('perfiles.json'):
        try:
            with open('perfiles.json', 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Error de Carga", f"Error al cargar el archivo de perfiles: {e}")
    return []

# --- Lógica de la Interfaz de Gestión de Perfiles ---
def gestionar_perfiles():
    """Crea y gestiona la ventana de Perfiles."""
    perfiles_menu = tk.Toplevel(root)
    perfiles_menu.title("Gestionar Perfiles")
    perfiles_menu.geometry("300x200")
    perfiles_menu.resizable(False, False)

    # Botones de la ventana de gestión de perfiles
    tk.Button(perfiles_menu, text="Ver Perfiles", command=ver_perfiles).pack(pady=10)
    tk.Button(perfiles_menu, text="Agregar Perfiles", command=agregar_perfil).pack(pady=10)
    tk.Button(perfiles_menu, text="Eliminar Perfiles", command=eliminar_perfil).pack(pady=10)

def ver_perfiles():
    """Muestra los perfiles guardados en un cuadro de mensaje."""
    perfiles = cargar_perfiles()
    if not perfiles:
        messagebox.showinfo("Ver Perfiles", "No hay perfiles guardados.")
        return

    perfiles_str = "\n".join([f"Origen: {p['origen']}\nDestino: {p['destino']}\nInclusiones: {', '.join(p['inclusiones'])}\nÚltimo Respaldo: {p['ultimo_respaldo'] or 'N/A'}\n" for p in perfiles])
    messagebox.showinfo("Perfiles Guardados", perfiles_str)

def agregar_perfil():
    """Crea y gestiona la ventana para agregar un nuevo perfil."""
    form_agregar_perfil = tk.Toplevel(root)
    form_agregar_perfil.title("Agregar Perfil")
    form_agregar_perfil.geometry("400x250")
    form_agregar_perfil.resizable(False, False)

    tk.Label(form_agregar_perfil, text="Path de Origen:").pack(pady=5)
    origen_entry = tk.Entry(form_agregar_perfil, width=50)
    origen_entry.pack(pady=5)

    tk.Label(form_agregar_perfil, text="Path de Destino:").pack(pady=5)
    destino_entry = tk.Entry(form_agregar_perfil, width=50)
    destino_entry.pack(pady=5)

    tk.Label(form_agregar_perfil, text="Inclusiones (separadas por coma):").pack(pady=5)
    inclusiones_entry = tk.Entry(form_agregar_perfil, width=50)
    inclusiones_entry.pack(pady=5)

    # Funciones para los botones del formulario
    def guardar():
        origen = origen_entry.get()
        destino = destino_entry.get()
        inclusiones = [inc.strip() for inc in inclusiones_entry.get().split(',') if inc.strip()]

        if not origen or not destino:
            messagebox.showerror("Error", "Los campos de origen y destino son obligatorios.")
            return

        nuevo_perfil = {
            "origen": origen,
            "destino": destino,
            "inclusiones": inclusiones,
            "ultimo_respaldo": None
        }

        perfiles = cargar_perfiles()
        perfiles.append(nuevo_perfil)
        guardar_perfiles(perfiles)
        messagebox.showinfo("Éxito", "Perfil guardado correctamente.")
        form_agregar_perfil.destroy()

    tk.Button(form_agregar_perfil, text="Guardar Perfil", command=guardar).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(form_agregar_perfil, text="Cancelar", command=form_agregar_perfil.destroy).pack(side=tk.RIGHT, padx=10, pady=10)

def eliminar_perfil():
    """Elimina el último perfil guardado para simplificar la demostración."""
    perfiles = cargar_perfiles()
    if not perfiles:
        messagebox.showinfo("Eliminar Perfil", "No hay perfiles para eliminar.")
        return

    if messagebox.askyesno("Confirmar", "¿Desea eliminar el último perfil guardado?"):
        perfiles.pop()
        guardar_perfiles(perfiles)
        messagebox.showinfo("Éxito", "Perfil eliminado correctamente.")

# --- Lógica de los Respaldos ---
def realizar_respaldo():
    """Inicia el proceso de respaldo incremental."""
    perfiles = cargar_perfiles()
    if not perfiles:
        messagebox.showerror("Error", "No hay perfiles guardados. Agregue uno primero.")
        return

    # Para este ejemplo, solo usamos el primer perfil
    perfil = perfiles[0]
    origen_path = perfil['origen']
    destino_base = perfil['destino']

    # Se comprueba la existencia de las rutas
    if not os.path.exists(origen_path):
        messagebox.showerror("Error de Ruta", f"La ruta de origen no existe: {origen_path}")
        return

    try:
        if not os.path.exists(destino_base):
            os.makedirs(destino_base)

        if perfil['ultimo_respaldo'] is None:
            # Primer respaldo: completo
            nombre_respaldo = datetime.now().strftime("Completo_%Y-%m-%d_%H-%M-%S")
            destino_final = os.path.join(destino_base, nombre_respaldo)
            
            messagebox.showinfo("Respaldo", f"Realizando el primer respaldo completo en: {destino_final}")
            shutil.copytree(origen_path, destino_final)
            
            perfil['ultimo_respaldo'] = datetime.now().isoformat()
            guardar_perfiles(perfiles)
            messagebox.showinfo("Respaldo Completo", "Respaldo inicial completado con éxito.")
            logging.info(f"Respaldo inicial completado en: {destino_final}")

        else:
            # Siguientes respaldos: incrementales
            nombre_respaldo = simpledialog.askstring("Nombre del Respaldo", "Ingrese el nombre para el respaldo incremental:")
            if not nombre_respaldo:
                return

            destino_final = os.path.join(destino_base, nombre_respaldo)
            if not os.path.exists(destino_final):
                os.makedirs(destino_final)

            ultimo_respaldo_dt = datetime.fromisoformat(perfil['ultimo_respaldo'])
            
            # Recorrer archivos y copiar solo los modificados
            archivos_a_copiar = []
            for dirpath, _, filenames in os.walk(origen_path):
                for filename in filenames:
                    origen_file = os.path.join(dirpath, filename)
                    if datetime.fromtimestamp(os.path.getmtime(origen_file)) > ultimo_respaldo_dt:
                        archivos_a_copiar.append(origen_file)
            
            if not archivos_a_copiar:
                messagebox.showinfo("Respaldo", "No se encontraron archivos modificados. Respaldo no realizado.")
                return

            # Actualizar la barra de progreso
            progress_bar.config(style="green.TProgressbar")
            for i, origen_file in enumerate(archivos_a_copiar):
                destino_file = origen_file.replace(origen_path, destino_final, 1)
                os.makedirs(os.path.dirname(destino_file), exist_ok=True)
                shutil.copy2(origen_file, destino_file)
                logging.info(f"Copiado (incremental): {origen_file}")

                progress = (i + 1) / len(archivos_a_copiar) * 100
                progress_bar["value"] = progress
                root.update_idletasks()
            
            perfil['ultimo_respaldo'] = datetime.now().isoformat()
            guardar_perfiles(perfiles)
            messagebox.showinfo("Éxito", "Respaldo incremental completado.")
            logging.info(f"Respaldo incremental completado en: {destino_final}")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error durante el respaldo: {e}")
    finally:
        progress_bar["value"] = 100
        root.update_idletasks()

def respaldo_consolidado():
    """Realiza un respaldo que solo mantiene la última versión de los archivos."""
    perfiles = cargar_perfiles()
    if not perfiles:
        messagebox.showerror("Error", "No hay perfiles guardados. Agregue uno primero.")
        return

    perfil = perfiles[0]
    origen_path = perfil['origen']
    destino_base = perfil['destino']
    
    destino_consolidado = os.path.join(destino_base, "Consolidado")

    if os.path.exists(destino_consolidado):
        if not messagebox.askyesno("Confirmar", "El respaldo consolidado ya existe. ¿Desea eliminar la versión anterior y crear una nueva?"):
            return
        shutil.rmtree(destino_consolidado)

    try:
        shutil.copytree(origen_path, destino_consolidado)
        messagebox.showinfo("Éxito", "Respaldo consolidado completado.")
        logging.info(f"Respaldo consolidado en: {destino_consolidado}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")


# --- Configuración de la Ventana Principal ---
root = tk.Tk()
root.title("Respaldos BUHO")
root.geometry("600x500")

# Cargar icono y imagen de fondo
try:
    root.iconbitmap("buho.ico")
    img = Image.open("buho.png")
    bg_image = ImageTk.PhotoImage(img)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception:
    logging.warning("No se pudo cargar el ícono o la imagen de fondo. Usando colores predeterminados.")
    root.configure(bg="#F0F0F0")

# Título y Frame de los botones (con fondo transparente simulado)
title_label = tk.Label(root, text="Respaldos BUHO", font=("Arial", 32, "bold"), bg="white")
title_label.pack(pady=20)

button_frame = tk.Frame(root, bg="white")
button_frame.pack(pady=10)

# Estilo para los botones
style = ttk.Style()
style.configure('TButton', font=('Arial', 12), background='white')
style.map('TButton', background=[('active', 'lightgray')])

# Botones principales (ahora usando `ttk.Button` para mejor apariencia)
btn_perfiles = ttk.Button(button_frame, text="Gestionar Perfiles", style='TButton', command=gestionar_perfiles)
btn_perfiles.pack(pady=5)

btn_respaldo = ttk.Button(button_frame, text="Realizar Respaldo", style='TButton', command=realizar_respaldo)
btn_respaldo.pack(pady=5)

btn_consolidado = ttk.Button(button_frame, text="Respaldo Consolidado", style='TButton', command=respaldo_consolidado)
btn_consolidado.pack(pady=5)

btn_salir = ttk.Button(button_frame, text="Salir", style='TButton', command=root.quit)
btn_salir.pack(pady=5)

# --- Barra de avance (con estilo verde) ---
# Usamos un estilo de ttk y lo configuramos de forma más robusta
progress_style = ttk.Style()
progress_style.theme_use('clam')  # 'clam' suele ser más limpio para estos cambios

# Creamos un nuevo estilo para el "elemento" interno de la barra de progreso
progress_style.layout('green.TProgressbar', 
                      [('clam.TProgressbar', {'children': 
                       [('clam.TProgressbar.trough', {'sticky': 'nswe', 'children': 
                         [('clam.TProgressbar.pbar', {'sticky': 'nswe'})]})]})])

# Configuramos el color de fondo del elemento que avanza
progress_style.configure('green.TProgressbar.pbar', background='green')

# Creamos la barra de progreso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", style="green.TProgressbar")
progress_bar.pack(pady=20)

# Iniciar el bucle de la aplicación
root.mainloop()