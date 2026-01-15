import sys
import threading # <--- ESTO ES LO QUE NOS PERMITE CORRER TODO JUNTO
import cv2
import pickle 
import face_recognition
import mysql.connector
import webbrowser 
from PyQt6 import uic, QtWidgets, QtGui, QtCore

# IMPORTAMOS TU PROYECTO FLASK
# Asumimos que tu archivo web se llama 'app.py' y la variable es 'app'
from app import app 

# --- HILO PARA EL SERVIDOR WEB ---
def correr_servidor_flask():
    # Desactivamos el reloader para que no cause conflictos con los hilos
    app.run(debug=False, port=5000, use_reloader=False)

# --- LÓGICA DE LA CÁMARA (PYQT) ---
def conectar_bd():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="apuesta"
    )

class SistemaBiometrico(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            uic.loadUi("interfaz.ui", self)
        except:
            QtWidgets.QMessageBox.critical(self, "Error", "Falta el archivo interfaz.ui")
            return
        
        self.btn_login.clicked.connect(self.proceso_login)
        self.btn_registro.clicked.connect(self.proceso_registro)
        
        self.cap = cv2.VideoCapture(0)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_img = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(qt_img))

    def proceso_registro(self):
        ret, frame = self.cap.read()
        if not ret: return
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not encodings:
            QtWidgets.QMessageBox.warning(self, "Error", "No detecto rostro.")
            return

        nombre, ok = QtWidgets.QInputDialog.getText(self, "Registro", "Usuario (Tal cual está en la BD):")
        if ok and nombre:
            try:
                db = conectar_bd()
                cursor = db.cursor()
                encoding_blob = pickle.dumps(encodings[0])
                sql = "INSERT INTO datos_biometricos (nombre_usuario, encoding) VALUES (%s, %s)"
                cursor.execute(sql, (nombre, encoding_blob))
                db.commit()
                QtWidgets.QMessageBox.information(self, "Éxito", "¡Rostro registrado!")
                cursor.close()
                db.close()
            except Exception as e:
                print(e)

    def proceso_login(self):
        ret, frame = self.cap.read()
        if not ret: return
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)

        if not encodings:
            QtWidgets.QMessageBox.warning(self, "Error", "No veo a nadie.")
            return
        
        encoding_actual = encodings[0]
        try:
            db = conectar_bd()
            cursor = db.cursor()
            cursor.execute("SELECT nombre_usuario, encoding FROM datos_biometricos")
            registros = cursor.fetchall()
            
            usuario_encontrado = None

            for nombre, blob in registros:
                encoding_guardado = pickle.loads(blob)
                if face_recognition.compare_faces([encoding_guardado], encoding_actual, tolerance=0.5)[0]:
                    usuario_encontrado = nombre
                    break
            
            if usuario_encontrado:
                QtWidgets.QMessageBox.information(self, "Acceso", f"Hola {usuario_encontrado}. Entrando...")
                # Abrimos la web que YA ESTÁ CORRIENDO en el hilo de fondo
                webbrowser.open(f"http://127.0.0.1:5000/login_facial/{usuario_encontrado}")
                self.close() # Cerramos la cámara
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "No reconocido.")
            cursor.close()
            db.close()
        except Exception as e:
            print(e)

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # 1. Arrancamos el servidor Flask en un hilo secundario (background)
    hilo_web = threading.Thread(target=correr_servidor_flask)
    hilo_web.daemon = True # Esto hace que se cierre cuando cerremos la ventana
    hilo_web.start()
    print("--- Servidor Web Iniciado en Segundo Plano ---")

    # 2. Arrancamos la Ventana PyQt (Frontend XML)
    app_qt = QtWidgets.QApplication(sys.argv)
    ventana = SistemaBiometrico()
    ventana.show()
    sys.exit(app_qt.exec())