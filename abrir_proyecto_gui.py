import subprocess
import os
import webbrowser
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, Checkbutton, filedialog, BooleanVar
from threading import Thread
import time
import socket

# Ruta a XAMPP
xampp_path = r"C:\xampp\xampp_start.exe"
xampp_stop_path = r'C:\xampp\xampp_stop.exe'
# Rutas a los proyectos de Laravel
laravel_project_path = r"C:\xampp\htdocs\ApiEstadia"
laravel_project_path_2 = r"C:\xampp\htdocs\ProyectoEstadia"
# Ruta al icono
icon_path = r'C:\xampp\htdocs\fav.ico'
# Ruta al archivo de IP
ip_update_script = r"C:\xampp\htdocs\ProyectoEstadia\config\ip.py"
# Ruta al ejecutable de MySQL en XAMPP
mysql_executable = r'C:\xampp\mysql\bin\mysql.exe'
# Ruta al script PHP de verificación
php_verify_script = r"C:\xampp\htdocs\verify_password.php"

# Flag to check if the project is already running
project_running = False

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # No se envía nada, se conecta a una IP pública para obtener la IP local
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Utiliza la IP local por defecto cuando no hay conexión a Internet
    finally:
        s.close()
    return ip

def update_env_file(ip):
    env_file = os.path.join(laravel_project_path_2, '.env')
    try:
        with open(env_file, 'r') as file:
            lines = file.readlines()
        
        with open(env_file, 'w') as file:
            for line in lines:
                if line.startswith('BACKEND_API'):
                    file.write(f'BACKEND_API="http://{ip}:8000"\n')
                else:
                    file.write(line)
        print(f"Archivo .env actualizado con la IP: {ip}")
    except Exception as e:
        print(f"Error al actualizar el archivo .env: {e}")

def abrir_xampp():
    try:
        subprocess.Popen(xampp_path, shell=True)
        print("XAMPP iniciado.")
    except Exception as e:
        print(f"Error al iniciar XAMPP: {e}")
        messagebox.showerror("Error", f"Error al iniciar XAMPP: {e}")

def abrir_laravel_proyecto(path, puerto, ip):
    try:
        os.chdir(path)
        subprocess.Popen(["cmd", "/K", f"php artisan serve --host={ip} --port={puerto}"], shell=True)
        print(f"Proyecto Laravel iniciado en {ip}:{puerto}.")
    except Exception as e:
        print(f"Error al iniciar el proyecto en {path}: {e}")
        messagebox.showerror("Error", f"Error al iniciar el proyecto en {path}: {e}")

def iniciar_proyecto():
    global project_running
    if project_running:
        messagebox.showwarning("Advertencia", "El proyecto ya está corriendo.")
        return

    waiting_window = Toplevel(root)
    waiting_window.title("Espera")
    waiting_window.geometry("300x100")
    waiting_window.iconbitmap(icon_path)
    waiting_window.configure(bg='#2b2b2b')
    Label(waiting_window, text="Espera mientras se abre el proyecto...", bg='#2b2b2b', fg='#ffffff', font=("Helvetica", 12)).pack(pady=20)
    
    root.update_idletasks()
    x = root.winfo_x()
    y = root.winfo_y()
    waiting_window.geometry(f"+{x + 100}+{y + 100}")

    def start_projects():
        global project_running
        ip = get_local_ip()
        update_env_file(ip)
        abrir_xampp()
        time.sleep(2)  # Reducido el tiempo de espera
        abrir_laravel_proyecto(laravel_project_path, 8000, ip)
        time.sleep(1)  # Reducido el tiempo de espera
        abrir_laravel_proyecto(laravel_project_path_2, 8001, ip)
        project_running = True
        waiting_window.destroy()
        messagebox.showinfo("Éxito", "Proyecto iniciado correctamente.")
        webbrowser.open(f"http://{ip}:8001")

    thread = Thread(target=start_projects)
    thread.start()

    # Centrar la ventana de mensaje con la pantalla principal
    waiting_window.update_idletasks()
    ww_width = waiting_window.winfo_width()
    ww_height = waiting_window.winfo_height()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root.winfo_x() + (root_width - ww_width) // 2
    y = root.winfo_y() + (root_height - ww_height) // 2
    waiting_window.geometry(f"{ww_width}x{ww_height}+{x}+{y}")

def is_process_running(process_name):
    try:
        result = subprocess.check_output(f'tasklist | findstr {process_name}', shell=True)
        return process_name in result.decode()
    except subprocess.CalledProcessError:
        return False

def cerrar_proyectos():
    global project_running
    try:
        php_running = is_process_running("php.exe")
        xampp_running = is_process_running("xampp-control.exe")  # Cambia "xampp-control.exe" por el nombre correcto si es diferente

        if not php_running and not xampp_running:
            messagebox.showinfo("Estado", "Ningún proyecto ni XAMPP están corriendo.")
            return

        def cerrar_xampp():
            if xampp_running:
                subprocess.Popen(xampp_stop_path, shell=True)
            else:
                print("XAMPP no está corriendo.")

        def cerrar_php():
            if php_running:
                subprocess.Popen("taskkill /f /im php.exe", shell=True)
            else:
                print("PHP no está corriendo.")
        
        # Crear y ejecutar subprocesos para cierre paralelo
        thread_xampp = Thread(target=cerrar_xampp)
        thread_php = Thread(target=cerrar_php)
        
        thread_xampp.start()
        thread_php.start()
        
        # Esperar a que ambos hilos terminen
        thread_xampp.join()
        thread_php.join()
        
        project_running = False
        messagebox.showinfo("Éxito", "Proyecto y XAMPP cerrados correctamente.")
        root.quit()  # Cierra la ventana principal y termina el programa
    except Exception as e:
        print(f"Error al cerrar los proyectos: {e}")
        messagebox.showerror("Error", f"Error al cerrar los proyectos: {e}")

def is_mysql_running():
    try:
        result = subprocess.check_output('tasklist | findstr mysqld', shell=True)
        return "mysqld.exe" in result.decode()
    except subprocess.CalledProcessError:
        return False

def importar_base_de_datos():
    if not is_mysql_running():  # Verifica si MySQL está corriendo
        messagebox.showerror("Error", "MySQL no está corriendo. Inicia el proyecto antes de importar la base de datos.")
        return
    
    def solicitar_contraseña():
        # Calcular la posición para centrar la ventana antes de crearla
        pw_width = 300
        pw_height = 150
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - pw_width) // 2
        y = (screen_height - pw_height) // 2

        password_window = Toplevel(root)
        password_window.title("Contraseña")
        password_window.geometry(f"{pw_width}x{pw_height}+{x}+{y}")
        password_window.iconbitmap(icon_path)
        password_window.configure(bg='#2b2b2b')

        Label(password_window, text="Introduce la contraseña:", bg='#2b2b2b', fg='#ffffff', font=("Helvetica", 12)).pack(pady=10)
        
        password_entry = Entry(password_window, show='*', bg='#1e1e1e', fg='#ffffff', font=("Helvetica", 12))
        password_entry.pack(pady=5)

        def toggle_password():
            if show_password.get():
                password_entry.config(show='')
            else:
                password_entry.config(show='*')

        show_password = BooleanVar()
        show_password_check = Checkbutton(password_window, text='Mostrar contraseña', variable=show_password, command=toggle_password, bg='#2b2b2b', fg='#ffffff', font=("Helvetica", 10))
        show_password_check.pack()

        def obtener_contraseña_bd():
            try:
                query = 'SELECT password FROM users WHERE role = 0;'
                command = f'{mysql_executable} -u root -e "{query}" api'
                result = subprocess.check_output(command, shell=True).decode().strip().split('\n')
                print(f"Resultado del comando MySQL: {result}")  # Agregado para depuración
                if len(result) > 1:
                    return result[1].strip()
                else:
                    return None
            except subprocess.CalledProcessError as e:
                print(f"Error al ejecutar el comando MySQL: {e}")
                return None

        def verificar_contraseña():
            password = password_entry.get()
            bd_password = obtener_contraseña_bd()
            if bd_password:
                try:
                    verify_command = f'php {php_verify_script} {password} {bd_password}'
                    verify_result = subprocess.check_output(verify_command, shell=True).decode().strip()
                    if verify_result == '1':
                        password_window.destroy()
                        file_path = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
                        if file_path:
                            importar_db(file_path)
                    else:
                        messagebox.showerror("Error", "Contraseña incorrecta.")
                        password_entry.delete(0, tk.END)
                except subprocess.CalledProcessError as e:
                    print(f"Error al ejecutar el comando PHP: {e}")
                    messagebox.showerror("Error", f"Error al verificar la contraseña: {e}")
            else:
                messagebox.showerror("Error", "No se pudo obtener la contraseña de la base de datos.")
                password_entry.delete(0, tk.END)

        btn_verificar = Button(password_window, text="Verificar", command=verificar_contraseña, bg='#2e8b57', fg='#ffffff', font=("Helvetica", 12), relief='flat', padx=20, pady=10)
        btn_verificar.pack(pady=10)
        
        password_window.transient(root)
        password_window.grab_set()
        root.wait_window(password_window)
    
    def importar_db(file_path):
        try:
            db_name = 'api'
            db_user = 'root'
            db_pass = ''

            # Crear la base de datos si no existe
            create_db_command = f'"{mysql_executable}" -u {db_user} -e "CREATE DATABASE IF NOT EXISTS {db_name};"'
            subprocess.run(create_db_command, shell=True)

            # Importar la base de datos
            import_command = f'"{mysql_executable}" -u {db_user} {db_name} < "{file_path}"'
            subprocess.run(import_command, shell=True)
            
            messagebox.showinfo("Éxito", "Base de datos creada e importada correctamente.")
        except Exception as e:
            print(f"Error al importar la base de datos: {e}")
            messagebox.showerror("Error", f"Error al importar la base de datos: {e}")

    solicitar_contraseña()

# Resto del código de la interfaz y lógica

root = tk.Tk()
root.title("Iniciar Proyecto Inventario")
root.geometry("500x300")

# Centrar la ventana principal en la pantalla
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 500) // 2
y = (screen_height - 300) // 2
root.geometry(f"500x300+{x}+{y}")
root.configure(bg='#1e1e1e')

try:
    root.iconbitmap(icon_path)
except Exception as e:
    print(f"Error al cargar el icono: {e}")
    messagebox.showerror("Error", f"Error al cargar el icono: {e}")

frame = tk.Frame(root, bg='#1e1e1e')
frame.pack(expand=True)

btn_iniciar = tk.Button(frame, text="Iniciar Proyecto", command=iniciar_proyecto, bg='#2e8b57', fg='#ffffff', font=("Helvetica", 12), relief='flat', padx=20, pady=10)
btn_iniciar.pack(pady=10)

btn_cerrar = tk.Button(frame, text="Cerrar Proyecto", command=cerrar_proyectos, bg='#b22222', fg='#ffffff', font=("Helvetica", 12), relief='flat', padx=20, pady=10)
btn_cerrar.pack(pady=10)

btn_importar_db = tk.Button(frame, text="Importar Base de Datos", command=importar_base_de_datos, bg='#4682b4', fg='#ffffff', font=("Helvetica", 12), relief='flat', padx=20, pady=10)
btn_importar_db.pack(pady=10)

root.mainloop()
