import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import shutil
from datetime import datetime
import json
import logging
from PIL import Image, ImageTk
import threading
import sys

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Función para obtener la ruta de los recursos en un ejecutable ---
def resource_path(relative_path):
    """Obtiene la ruta absoluta a los recursos, útil para PyInstaller."""
    try:
        # PyInstaller crea un atributo _MEIPASS para la ruta temporal
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Funciones Auxiliares de Perfiles ---
def guardar_perfiles(perfiles):
    """Guarda la lista de perfiles en un archivo JSON."""
    try:
        # Usa la ruta correcta para guardar el archivo
        with open(resource_path('perfiles.json'), 'w') as f:
            json.dump(perfiles, f, indent=4)
    except IOError as e:
        messagebox.showerror("Error de Guardado", f"No se pudo guardar el archivo de perfiles: {e}")

def cargar_perfiles():
    """Carga los perfiles desde un archivo JSON. Si no existe, devuelve una lista vacía."""
    perfiles_path = resource_path('perfiles.json')
    if os.path.exists(perfiles_path):
        try:
            with open(perfiles_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Error de Carga", f"Error al cargar el archivo de perfiles: {e}")
            return []
    return []

# --- Lógica de la Interfaz de Gestión de Perfiles ---
def gestionar_perfiles():
    """Crea y gestiona la ventana de Perfiles."""
    perfiles_menu = tk.Toplevel(root)
    perfiles_menu.title("Gestionar Perfiles")
    perfiles_menu.geometry("300x200")
    perfiles_menu.resizable(False, False)
    center_window(perfiles_menu, 300, 200)

    limpiar_barra()
    
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

    limpiar_barra()
    
    # Usamos .get('exclusiones', []) para manejar perfiles antiguos que no tienen la clave
    perfiles_str = "\n".join([f"Origen: {p['origen']}\nDestino: {p['destino']}\nExclusiones: {', '.join(p.get('exclusiones', []))}\nÚltimo Respaldo: {p['ultimo_respaldo'] or 'N/A'}\n" for p in perfiles])
    messagebox.showinfo("Perfiles Guardados", perfiles_str)

def agregar_perfil():
    """Crea y gestiona la ventana para agregar un nuevo perfil, con buscadores de carpetas."""
    form_agregar_perfil = tk.Toplevel(root)
    form_agregar_perfil.title("Agregar Perfil")
    form_agregar_perfil.geometry("500x250")
    form_agregar_perfil.resizable(False, False)
    center_window(form_agregar_perfil, 500, 250)

    limpiar_barra()

    # --- Funciones para abrir los buscadores de carpetas ---
    def buscar_origen():
        ruta = filedialog.askdirectory()
        if ruta:
            origen_entry.delete(0, tk.END)
            origen_entry.insert(0, ruta)

    def buscar_destino():
        ruta = filedialog.askdirectory()
        if ruta:
            destino_entry.delete(0, tk.END)
            destino_entry.insert(0, ruta)
    # --- Fin de las funciones de búsqueda ---

    tk.Label(form_agregar_perfil, text="Path de Origen:").pack(pady=5)
    frame_origen = tk.Frame(form_agregar_perfil)
    frame_origen.pack()
    origen_entry = tk.Entry(frame_origen, width=40)
    origen_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(frame_origen, text="Buscar", command=buscar_origen).pack(side=tk.LEFT)

    tk.Label(form_agregar_perfil, text="Path de Destino:").pack(pady=5)
    frame_destino = tk.Frame(form_agregar_perfil)
    frame_destino.pack()
    destino_entry = tk.Entry(frame_destino, width=40)
    destino_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(frame_destino, text="Buscar", command=buscar_destino).pack(side=tk.LEFT)

    tk.Label(form_agregar_perfil, text="Exclusiones (separadas por coma):").pack(pady=5)
    exclusiones_entry = tk.Entry(form_agregar_perfil, width=50)
    exclusiones_entry.pack(pady=5)

    def guardar():
        origen = origen_entry.get()
        destino = destino_entry.get()
        exclusiones = [exc.strip() for exc in exclusiones_entry.get().split(',') if exc.strip()]

        if not origen or not destino:
            messagebox.showerror("Error", "Los campos de origen y destino son obligatorios.")
            return

        nuevo_perfil = {
            "origen": origen,
            "destino": destino,
            "exclusiones": exclusiones,
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

    limpiar_barra()
    
    if messagebox.askyesno("Confirmar", "¿Desea eliminar el último perfil guardado?"):
        perfiles.pop()
        guardar_perfiles(perfiles)
        messagebox.showinfo("Éxito", "Perfil eliminado correctamente.")

# --- Lógica de los Respaldos ---
def realizar_respaldo():
    """Muestra una lista de perfiles guardados para que el usuario elija uno para el respaldo incremental."""
    perfiles = cargar_perfiles()
    if not perfiles:
        messagebox.showerror("Error", "No hay perfiles guardados. Agregue uno primero.")
        return
        
    limpiar_barra()

    def iniciar_respaldo_hilo(perfiles_actualizados, perfil, nombre_respaldo):
        origen_path = perfil['origen']
        destino_base = perfil['destino']
        exclusiones = perfil.get('exclusiones', [])
        
        # Lista para almacenar todos los archivos a copiar
        archivos_a_copiar = []
        try:
            if not os.path.exists(origen_path):
                messagebox.showerror("Error de Ruta", f"La ruta de origen no existe: {origen_path}")
                return

            # Actualizar la etiqueta de estado antes de empezar
            estado_label.config(text=f"Respaldo en curso...\nDe: {origen_path}\nA: {destino_base}")
            root.update_idletasks()

            if not nombre_respaldo: # Respaldo Completo
                nombre_respaldo = datetime.now().strftime("Completo_%Y-%m-%d_%H-%M-%S")
                destino_final = os.path.join(destino_base, nombre_respaldo)

                # Primero, contamos todos los archivos para el progreso
                for dirpath, dirnames, filenames in os.walk(origen_path):
                    dirnames[:] = [d for d in dirnames if d not in exclusiones]
                    for filename in filenames:
                        if filename not in exclusiones:
                            archivos_a_copiar.append(os.path.join(dirpath, filename))
                
                if not archivos_a_copiar:
                    messagebox.showinfo("Respaldo", "No se encontraron archivos para el respaldo completo.")
                    return

                # Configuración de la barra de progreso
                progress_bar.config(mode="determinate")

                # Ahora, copiamos los archivos y actualizamos la barra
                for i, origen_file in enumerate(archivos_a_copiar):
                    destino_file = origen_file.replace(origen_path, destino_final, 1)
                    os.makedirs(os.path.dirname(destino_file), exist_ok=True)
                    shutil.copy2(origen_file, destino_file)
                    
                    progress = (i + 1) / len(archivos_a_copiar) * 100
                    progress_bar["value"] = progress
                    root.update_idletasks() # Actualiza la interfaz

                perfil['ultimo_respaldo'] = datetime.now().isoformat()
                guardar_perfiles(perfiles_actualizados)
                
                messagebox.showinfo("Respaldo Completo", "Respaldo inicial completado con éxito.")
                logging.info(f"Respaldo inicial completado en: {destino_final}")
            
            else: # Respaldo incremental
                destino_final = os.path.join(destino_base, nombre_respaldo)
                if not os.path.exists(destino_final):
                    os.makedirs(destino_final)

                ultimo_respaldo_dt = datetime.fromisoformat(perfil['ultimo_respaldo'])
                
                for dirpath, dirnames, filenames in os.walk(origen_path):
                    dirnames[:] = [d for d in dirnames if d not in exclusiones]
                    for filename in filenames:
                        if filename in exclusiones:
                            continue
                        origen_file = os.path.join(dirpath, filename)
                        if datetime.fromtimestamp(os.path.getmtime(origen_file)) > ultimo_respaldo_dt:
                            archivos_a_copiar.append(origen_file)
                
                if not archivos_a_copiar:
                    messagebox.showinfo("Respaldo", "No se encontraron archivos modificados. Respaldo no realizado.")
                    return

                # Configuración de la barra de progreso
                progress_bar.config(mode="determinate")
                
                for i, origen_file in enumerate(archivos_a_copiar):
                    if any(os.path.basename(os.path.dirname(origen_file)) == excl for excl in exclusiones):
                        continue

                    destino_file = origen_file.replace(origen_path, destino_final, 1)
                    os.makedirs(os.path.dirname(destino_file), exist_ok=True)
                    shutil.copy2(origen_file, destino_file)
                    
                    progress = (i + 1) / len(archivos_a_copiar) * 100
                    progress_bar["value"] = progress
                    root.update_idletasks() # Actualiza la interfaz
                
                perfil['ultimo_respaldo'] = datetime.now().isoformat()
                guardar_perfiles(perfiles_actualizados)
                messagebox.showinfo("Éxito", "Respaldo incremental completado.")
                logging.info(f"Respaldo incremental completado en: {destino_final}")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante el respaldo: {e}")
        finally:
            progress_bar["value"] = 100
            root.update_idletasks()
            limpiar_barra()
    
    def on_select():
        try:
            seleccion = listbox.curselection()[0]
            perfiles_actualizados = cargar_perfiles()
            perfil_seleccionado = perfiles_actualizados[seleccion]
            
            existe_completo = False
            if os.path.exists(perfil_seleccionado['destino']):
                for dir_name in os.listdir(perfil_seleccionado['destino']):
                    if dir_name.startswith("Completo_"):
                        existe_completo = True
                        break
            
            nombre_respaldo = None
            if existe_completo:
                nombre_respaldo = simpledialog.askstring("Nombre del Respaldo", "Ingrese el nombre para el respaldo incremental:")
                if not nombre_respaldo:
                    return

            menu_perfiles.destroy()
            thread = threading.Thread(target=iniciar_respaldo_hilo, args=(perfiles_actualizados, perfil_seleccionado, nombre_respaldo))
            thread.start()

        except IndexError:
            messagebox.showerror("Error de Selección", "Por favor, seleccione un perfil de la lista.")

    menu_perfiles = tk.Toplevel(root)
    menu_perfiles.title("Seleccionar Perfil")
    menu_perfiles.geometry("400x300")
    center_window(menu_perfiles, 400, 300)
    
    tk.Label(menu_perfiles, text="Seleccione un perfil para el respaldo:").pack(pady=10)
    frame_lista = tk.Frame(menu_perfiles)
    frame_lista.pack(fill=tk.BOTH, expand=True)
    listbox = tk.Listbox(frame_lista, selectmode=tk.SINGLE)
    for i, p in enumerate(perfiles):
        listbox.insert(tk.END, f"{i+1}. {os.path.basename(p['origen'])} -> {os.path.basename(p['destino'])}")
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    tk.Button(menu_perfiles, text="Realizar Respaldo", command=on_select).pack(pady=10)

def respaldo_consolidado():
    """Muestra una lista de perfiles guardados para que el usuario elija uno para el respaldo consolidado."""
    perfiles = cargar_perfiles()
    if not perfiles:
        messagebox.showerror("Error", "No hay perfiles guardados. Agregue uno primero.")
        return

    limpiar_barra()

    def iniciar_consolidado(indice_perfil):
        perfil = perfiles[indice_perfil]
        origen_path = perfil['origen']
        destino_base = perfil['destino']
        exclusiones = perfil.get('exclusiones', [])

        menu_perfiles.destroy()
        
        if not messagebox.askyesno("Confirmar Respaldo Consolidado", f"¿Está seguro de que desea realizar un respaldo consolidado del perfil:\n{origen_path} ?"):
            return

        destino_consolidado = os.path.join(destino_base, "Consolidado")

        if os.path.exists(destino_consolidado):
            if not messagebox.askyesno("Confirmar", "El respaldo consolidado ya existe. ¿Desea eliminar la versión anterior y crear una nueva?"):
                return
            shutil.rmtree(destino_consolidado)

        try:
            shutil.copytree(origen_path, destino_consolidado, ignore=shutil.ignore_patterns(*exclusiones))
            messagebox.showinfo("Éxito", "Respaldo consolidado completado.")
            logging.info(f"Respaldo consolidado en: {destino_consolidado}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    menu_perfiles = tk.Toplevel(root)
    menu_perfiles.title("Seleccionar Perfil")
    menu_perfiles.geometry("400x300")
    center_window(menu_perfiles, 400, 300)
    
    tk.Label(menu_perfiles, text="Seleccione un perfil para el respaldo consolidado:").pack(pady=10)
    frame_lista = tk.Frame(menu_perfiles)
    frame_lista.pack(fill=tk.BOTH, expand=True)
    listbox = tk.Listbox(frame_lista, selectmode=tk.SINGLE)
    for i, p in enumerate(perfiles):
        listbox.insert(tk.END, f"{i+1}. {os.path.basename(p['origen'])} -> {os.path.basename(p['destino'])}")
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    
    def on_select():
        try:
            seleccion = listbox.curselection()[0]
            iniciar_consolidado(seleccion)
        except IndexError:
            messagebox.showerror("Error de Selección", "Por favor, seleccione un perfil de la lista.")

    tk.Button(menu_perfiles, text="Realizar Respaldo", command=on_select).pack(pady=10)

# --- Función para limpiar la barra de progreso y la etiqueta de estado ---
def limpiar_barra():
    progress_bar.stop()
    progress_bar["value"] = 0
    progress_bar.config(mode="determinate")
    estado_label.config(text="") # Limpia la etiqueta
    root.update_idletasks()

# --- Función para centrar la ventana ---
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

# --- Configuración de la Ventana Principal ---
root = tk.Tk()
root.title("Respaldos BUHO")
root.geometry("600x500")

center_window(root, 600, 500)

# Cargar la imagen de fondo y el ícono
try:
    # Usamos la función resource_path para encontrar los archivos
    root.iconbitmap(resource_path("buho.ico"))
    
    original_image = Image.open(resource_path("buho.png"))
    bg_image = ImageTk.PhotoImage(original_image)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def on_resize(event):
        global bg_image
        if event.width > 0 and event.height > 0:
            resized_image = original_image.resize((event.width, event.height), Image.Resampling.LANCZOS)
            bg_image = ImageTk.PhotoImage(resized_image)
            bg_label.config(image=bg_image)
    root.bind("<Configure>", on_resize)

except Exception:
    logging.warning("No se pudo cargar el ícono o la imagen de fondo. Usando colores predeterminados.")
    root.configure(bg="#F0F0F0")

title_label = tk.Label(root, text="Respaldos BUHO", font=("Arial", 32, "bold"), bg="white")
title_label.pack(pady=20)

button_frame = tk.Frame(root, bg="white")
button_frame.pack(pady=10)

style = ttk.Style()
style.configure('TButton', font=('Arial', 12), background='white')
style.map('TButton', background=[('active', 'lightgray')])

btn_perfiles = ttk.Button(button_frame, text="Gestionar Perfiles", style='TButton', command=gestionar_perfiles)
btn_perfiles.pack(pady=5)
btn_respaldo = ttk.Button(button_frame, text="Realizar Respaldo", style='TButton', command=realizar_respaldo)
btn_respaldo.pack(pady=5)
btn_consolidado = ttk.Button(button_frame, text="Respaldo Consolidado", style='TButton', command=respaldo_consolidado)
btn_consolidado.pack(pady=5)
btn_salir = ttk.Button(button_frame, text="Salir", style='TButton', command=root.quit)
btn_salir.pack(pady=5)

progress_style = ttk.Style()
progress_style.theme_use('clam')
progress_style.configure('TProgressbar', background='green', troughcolor='#ccc')

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=20)

# Etiqueta para mostrar el estado del respaldo
estado_label = tk.Label(root, text="", font=("Arial", 10), bg="white")
estado_label.pack(pady=5)

root.mainloop()