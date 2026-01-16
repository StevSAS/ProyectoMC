import threading
import webbrowser
import time
import os
import sys
from threading import Thread

# 1. Importamos tu servidor arreglado (app.py)
try:
    from app import app
except ImportError:
    print("❌ ERROR: No encuentro 'app.py'.")
    time.sleep(5)
    sys.exit()

def arrancar_servidor():
    """
    Arranca el servidor Flask en segundo plano.
    Usamos el puerto 5000 (el que te funciona) y threaded=True para evitar bloqueos.
    """
    print("🚀 Iniciando Motor BETUTM en Puerto 5000...")
    # CAMBIO REALIZADO: Puerto 5000
    app.run(port=5000, debug=False, threaded=True, use_reloader=False)

def abrir_modo_app():
    """
    Abre la interfaz en una ventana limpia tipo 'Aplicación de Escritorio'
    usando el motor de Chrome/Edge instalado en el sistema.
    """
    # Damos tiempo al servidor para que arranque
    time.sleep(2)
    
    # CAMBIO REALIZADO: Apuntamos al puerto 5000
    url = "http://localhost:5000"
    print("🖥️ Abriendo Ventana de Aplicación...")

    # Rutas comunes de Google Chrome
    rutas_chrome = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    
    chrome_encontrado = None

    # Buscamos dónde está instalado Chrome
    for ruta in rutas_chrome:
        ruta_real = os.path.expandvars(ruta)
        if os.path.exists(ruta_real):
            chrome_encontrado = ruta_real
            break
    
    if chrome_encontrado:
        # EL TRUCO DE MAGIA: --app=URL
        # Esto abre la web sin barras de navegación, pareciendo una app nativa.
        os.system(f'"{chrome_encontrado}" --app={url} --window-size=1200,800')
    else:
        # Si no hay Chrome, usamos el navegador por defecto
        webbrowser.open(url)

if __name__ == "__main__":
    # A. Arrancamos el servidor en un hilo paralelo (El Cerebro)
    hilo_server = Thread(target=arrancar_servidor)
    hilo_server.daemon = True # Se apaga cuando cierras la ventana
    hilo_server.start()

    # B. Abrimos la ventana visual (La Cara)
    abrir_modo_app()
    
    # C. Mantenemos el programa vivo esperando
    print("✅ Sistema Operativo. Presiona Ctrl+C en esta terminal para cerrar.")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Cerrando sistema...")
            break