import sys
import cv2
import pickle 
import face_recognition
import mysql.connector
import webbrowser 
from PyQt6 import uic, QtWidgets, QtGui, QtCore

# --- CONEXIÓN BD ---
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
            print("Error: Falta interfaz.ui")
            return
        
        # Conectar los DOS botones a funciones diferentes
        self.btn_login.clicked.connect(self.proceso_login)
        self.btn_registro.clicked.connect(self.proceso_registro)
        
        # Cámara
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

    # --- OPCIÓN 1: REGISTRAR UNA CARA NUEVA ---
    def proceso_registro(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not encodings:
            QtWidgets.QMessageBox.warning(self, "Error", "No detecto ningún rostro. Ponte frente a la cámara.")
            return

        # Pedir el nombre del usuario tal cual está en la base de datos
        nombre, ok = QtWidgets.QInputDialog.getText(self, "Vincular Cuenta", "Escribe tu Usuario EXACTO (ej: jose):")
        
        if ok and nombre:
            try:
                db = conectar_bd()
                cursor = db.cursor()
                
                # Opcional: Verificar si el usuario existe en la tabla usuarios antes de guardar la cara
                # cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (nombre,))
                # if not cursor.fetchone():
                #    QtWidgets.QMessageBox.warning(self, "Error", "Ese usuario no existe.")
                #    return

                # Guardamos la cara
                encoding_blob = pickle.dumps(encodings[0])
                sql = "INSERT INTO datos_biometricos (nombre_usuario, encoding) VALUES (%s, %s)"
                cursor.execute(sql, (nombre, encoding_blob))
                db.commit()
                
                QtWidgets.QMessageBox.information(self, "Éxito", f"¡Cara de '{nombre}' registrada correctamente!")
                cursor.close()
                db.close()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error en BD: {e}")

    # --- OPCIÓN 2: INICIAR SESIÓN ---
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
            
            usuario_identificado = None

            for nombre, blob in registros:
                encoding_guardado = pickle.loads(blob)
                # Comparamos
                match = face_recognition.compare_faces([encoding_guardado], encoding_actual, tolerance=0.5)[0]
                if match:
                    usuario_identificado = nombre
                    break
            
            if usuario_identificado:
                QtWidgets.QMessageBox.information(self, "Bienvenido", f"Hola {usuario_identificado}. Abriendo sistema...")
                # Lanza el navegador y entra directo
                webbrowser.open(f"http://127.0.0.1:3000/login_facial/{usuario_identificado}")
                self.close()
            else:
                QtWidgets.QMessageBox.warning(self, "Denegado", "Rostro no reconocido. Regístrate primero.")
            
            cursor.close()
            db.close()

        except Exception as e:
            print(e)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = SistemaBiometrico()
    ventana.show()
    sys.exit(app.exec())