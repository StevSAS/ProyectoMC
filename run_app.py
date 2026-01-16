import threading
import webbrowser
import time
import os
import sys
from threading import Thread

# 1. Importamos tu servidor (app.py)
try:
    from app import app
except ImportError:
    print("❌ ERROR: No encuentro 'app.py'.")
    time.sleep(5)
    sys.exit()

def arrancar_servidor():
    """
    Arranca el servidor en el puerto 5000 con hilos (threaded=True)
    para que no se cierre la app al usar la cámara.
    """
    print("🚀 Iniciando Sistema BETUTM...")
    # USAMOS PUERTO 5000 Y THREADED=TRUE (La configuración segura)
    app.run(port=5000, debug=False, threaded=True, use_reloader=False)

def abrir_modo_app():
    """
    Abre la ventana tipo aplicación usando Chrome/Edge
    """
    time.sleep(2) # Esperamos a que arranque el servidor
    
    url = "http://localhost:5000"
    print("🖥️ Abriendo Interfaz...")

    # Buscamos Google Chrome
    rutas_chrome = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    
    chrome_path = None

    for ruta in rutas_chrome:
        ruta_real = os.path.expandvars(ruta)
        if os.path.exists(ruta_real):
            chrome_path = ruta_real
            break
    
    if chrome_path:
        # Abrimos en MODO APP (Sin pestañas, parece programa de escritorio)
        os.system(f'"{chrome_path}" --app={url} --window-size=1200,800')
    else:
        # Si no hay Chrome, abre el navegador normal
        webbrowser.open(url)

if __name__ == "__main__":
    # A. Hilo del Servidor
    hilo_server = Thread(target=arrancar_servidor)
    hilo_server.daemon = True
    hilo_server.start()

    # B. Abrir Ventana
    abrir_modo_app()
    
    # C. Mantener vivo
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break