import json
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_mysqldb import MySQL
import cv2
import face_recognition
import pickle
import numpy as np
from threading import Lock
lock = Lock()
camera = cv2.VideoCapture(0)

app = Flask(__name__)

# --- CONFIGURACIÓN MYSQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'apuesta'
mysql = MySQL(app)

app.secret_key = "mysecretkey"

# ==========================================
#  VARIABLES GLOBALES Y CÁMARA
# ==========================================
global_frame = None

def generar_frames():
    global global_frame
    
    while True:
        # 🛡️ PROTECCIÓN TOTAL: Bloqueamos la cámara mientras leemos
        # Así nadie más la toca y evitamos el choque que cierra el programa.
        with lock:
            success, frame = camera.read()
            if success:
                global_frame = frame.copy()

        if not success:
            break
        else:
            # Codificamos la imagen para enviarla
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
    # NOTA: Aquí NO ponemos 'camera.release()'. 
    # La cámara se queda encendida siempre para que no falle al cambiar de página.
@app.route('/video_feed')
def video_feed():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ==========================================
#  RUTAS PRINCIPALES
# ==========================================
@app.route('/')
def Index():
    if 'id_usuario' in session: return redirect(url_for('panel'))
    return render_template('principal.html')

@app.route('/registrarse')
def registrarse(): return render_template('registro.html')

@app.route('/agregar_usuario', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contraseña = request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (nombre, apellido, email, contraseña, saldo, fecha_registro) VALUES (%s, %s, %s, %s, 0, NOW())", (nombre, apellido, email, contraseña))
        mysql.connection.commit()
        flash("Usuario registrado correctamente")
        return redirect(url_for('Index'))

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usuario, nombre, saldo, rol FROM usuarios WHERE email=%s AND contraseña=%s", (email, contraseña))
        user = cur.fetchone()
        if user:
            session['id_usuario'] = user[0]
            session['nombre'] = user[1]
            session['saldo'] = float(user[2])
            session['rol'] = user[3]
            return redirect(url_for('panel'))
        else:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for('Index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Index'))

# --- 🚀 FUNCIÓN PANEL ACTUALIZADA 🚀 ---
@app.route('/panel')
def panel():
    if 'id_usuario' not in session: return redirect(url_for('Index'))
    
    id_usuario = session['id_usuario']
    nombre_usuario = session['nombre'] # Necesario para buscar el rostro
    
    cur = mysql.connection.cursor()
    
    # 1. Actualizar Saldo
    cur.execute("SELECT saldo FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    res = cur.fetchone()
    if res: session['saldo'] = float(res[0])
    
    # 2. Cargar Partidos
    cur.execute("SELECT * FROM partidos")
    columnas = [d[0] for d in cur.description]
    partidos_db = [dict(zip(columnas, row)) for row in cur.fetchall()]
    lista_final = []
    for p in partidos_db:
        p['cuotas'] = {'1': p['cuota_1'], 'X': p['cuota_x'], '2': p['cuota_2']}
        lista_final.append(p)

    # 3. VERIFICAR SI YA TIENE ROSTRO (NUEVO)
    # Buscamos en la tabla de caras si existe el nombre de este usuario
    cur.execute("SELECT nombre_usuario FROM datos_biometricos WHERE nombre_usuario = %s", (nombre_usuario,))
    datos_rostro = cur.fetchone()
    
    # Si encuentra datos, es True (tiene cara). Si no, es False.
    tiene_rostro = True if datos_rostro else False

    # 4. Enviamos la variable 'tiene_rostro' al HTML
    return render_template("panel.html", 
                        partidos=lista_final, 
                        saldo=session['saldo'], 
                        nombre=session['nombre'],
                        tiene_rostro=tiene_rostro)

# ==========================================
#  SISTEMA BIOMÉTRICO (CON SEGURIDAD ANTI-DUPLICADOS)
# ==========================================

@app.route('/vista_registro_facial')
def vista_registro_facial():
    if 'id_usuario' not in session: return redirect(url_for('login')) 
    return render_template('registro_facial.html')

@app.route('/vista_login_facial')
def vista_login_facial():
    return render_template('login_facial.html')

@app.route('/guardar_rostro_db', methods=['POST'])
def guardar_rostro_db():
    global global_frame
    
    # 1. Seguridad: Verificar si el usuario inició sesión antes de registrar su cara
    if 'nombre' not in session:
        flash("⚠️ Inicia sesión primero para registrar tu rostro.")
        return redirect(url_for('Index'))

    nombre_usuario = session['nombre']
    frame_local = None
    
    with lock:
        if global_frame is not None:
            frame_local = global_frame.copy()

    if frame_local is None:
        flash("❌ Cámara no lista. Intenta de nuevo.")
        return redirect(url_for('vista_registro_facial'))

    try:
        # --- CORRECCIÓN DEL ERROR DE IMAGEN (Igual que hicimos ayer) ---
        # 1. Convertir BGR a RGB
        rgb_frame = cv2.cvtColor(frame_local, cv2.COLOR_BGR2RGB)
        
        # 2. MEDICINA: Limpiamos la memoria de la imagen para que dlib no falle
        rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)
        # ---------------------------------------------------------------

        # 3. Detectar rostro
        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not encodings:
            flash("❌ No veo ninguna cara. Acércate más y evita contraluz.")
            return redirect(url_for('vista_registro_facial'))

        # 4. Guardar en Base de Datos
        nuevo_encoding = encodings[0]
        blob = pickle.dumps(nuevo_encoding)

        cur = mysql.connection.cursor()
        # Verificar duplicados (Opcional: evitar que una cara se registre 2 veces)
        cur.execute("SELECT nombre_usuario, encoding FROM datos_biometricos")
        usuarios = cur.fetchall()
        
        for user_db, blob_db in usuarios:
            if blob_db:
                known_enc = pickle.loads(blob_db)
                if face_recognition.compare_faces([known_enc], nuevo_encoding, tolerance=0.5)[0]:
                    if user_db != nombre_usuario:
                        flash(f"⛔ Esa cara ya pertenece al usuario '{user_db}'.")
                        return redirect(url_for('vista_registro_facial'))

        # Insertar o Actualizar
        cur.execute("DELETE FROM datos_biometricos WHERE nombre_usuario = %s", (nombre_usuario,))
        cur.execute("INSERT INTO datos_biometricos (nombre_usuario, encoding) VALUES (%s, %s)", (nombre_usuario, blob))
        mysql.connection.commit()

        flash(f"✅ ¡Éxito! Rostro vinculado a {nombre_usuario}.")
        return redirect(url_for('panel'))

    except Exception as e:
        print(f"ERROR TÉCNICO EN REGISTRO: {e}")
        flash("❌ Error técnico al procesar la imagen.")
        return redirect(url_for('vista_registro_facial'))
    
@app.route('/verificar_rostro_db', methods=['POST'])
def verificar_rostro_db():
    global global_frame
    frame_local = None
    
    # 1. Copia segura de la imagen (usando el candado)
    with lock:
        if global_frame is not None:
            frame_local = global_frame.copy()
    
    if frame_local is None:
        flash("⏳ La cámara se está iniciando... intenta de nuevo.")
        return redirect(url_for('vista_login_facial'))

    try:
        # --- PROCESAMIENTO DE IMAGEN (Tu lógica excelente) ---
        ret, buffer = cv2.imencode('.jpg', frame_local)
        frame_limpio = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

        encodings = []
        
        # Intento 1: Color
        try:
            rgb_frame = cv2.cvtColor(frame_limpio, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            if face_locations:
                encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        except Exception:
            pass # Si falla color, seguimos silenciosamente al B/N

        # Intento 2: Blanco y Negro (Si falló el anterior o no detectó nada)
        if not encodings:
            print("⚠️ Usando modo respaldo Blanco y Negro...")
            gray_frame = cv2.cvtColor(frame_limpio, cv2.COLOR_BGR2GRAY)
            face_locations = face_recognition.face_locations(gray_frame)
            rgb_fake = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
            if face_locations:
                encodings = face_recognition.face_encodings(rgb_fake, face_locations)

        if not encodings:
            flash("❌ No veo tu rostro. Acércate más a la cámara.")
            return redirect(url_for('vista_login_facial'))
        
        encoding_actual = encodings[0]
        
        # --- BASE DE DATOS (Corregido para no colgarse) ---
        cur = mysql.connection.cursor()
        usuario_encontrado = None
        
        try:
            cur.execute("SELECT nombre_usuario, encoding FROM datos_biometricos")
            data = cur.fetchall()
            
            # Buscar coincidencia
            for nombre, blob in data:
                if blob:
                    encoding_guardado = pickle.loads(blob)
                    # Tolerancia 0.5 es estricta (buena seguridad), 0.6 es estándar
                    match = face_recognition.compare_faces([encoding_guardado], encoding_actual, tolerance=0.5)
                    if match[0]:
                        usuario_encontrado = nombre
                        break
            
            if usuario_encontrado:
                # Buscamos los datos completos del usuario
                cur.execute("SELECT id_usuario, nombre, saldo, rol FROM usuarios WHERE nombre = %s", (usuario_encontrado,))
                user = cur.fetchone()
                
                if user:
                    # Guardamos variables de sesión
                    session['loggedin'] = True  # <--- IMPORTANTE PARA EL PANEL
                    session['id_usuario'] = user[0]
                    session['id'] = user[0]     # Por si usas 'id' en otro lado
                    session['nombre'] = user[1]
                    session['saldo'] = float(user[2])
                    session['rol'] = user[3]
                    
                    flash(f"✅ ¡Hola de nuevo, {user[1]}!")
                    return redirect(url_for('panel'))
            
            # Si llegamos aquí, no hubo coincidencia
            flash("⛔ Rostro no registrado.")
            return redirect(url_for('vista_login_facial'))

        finally:
            # ESTO ES LO QUE TE FALTABA: Cerrar la puerta al salir
            cur.close() 

    except Exception as e:
        print(f"❌ Error crítico en verificación: {e}")
        flash("❌ Error del sistema.")
        return redirect(url_for('vista_login_facial'))
    # ==========================================
#  OTRAS RUTAS
# ==========================================
@app.route('/recargar')
def recargar():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    return render_template('recargar.html')

@app.route('/guardar_recarga', methods=['POST'])
def guardar_recarga():
    if 'id_usuario' not in session: return redirect(url_for('login'))
    id_usuario = session['id_usuario']
    monto = float(request.form['monto'])
    metodo = request.form['metodo']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO recarga (id_usuario, monto, metodo, fecha) VALUES (%s, %s, %s, NOW())", (id_usuario, monto, metodo))
    cur.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id_usuario = %s", (monto, id_usuario))
    mysql.connection.commit()
    session['saldo'] += monto
    flash(f"Recarga de ${monto} realizada con éxito")
    return redirect(url_for('panel'))

@app.route('/procesar_apuesta', methods=['POST'])
def procesar_apuesta():
    if 'id_usuario' not in session: return redirect(url_for('Index'))
    monto = float(request.form.get('monto_apuesta'))
    id_usuario = session['id_usuario']
    lista_apuestas = json.loads(request.form.get('datos_apuestas'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT saldo FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    saldo_actual = float(cur.fetchone()[0])
    if monto > saldo_actual:
        flash("❌ Saldo insuficiente")
        return redirect(url_for('panel'))
    cuota_total = 1
    for apuesta in lista_apuestas:
        # TRUCO DE MAGIA: Si viene '3,20', lo convertimos a '3.20'
        valor_str = str(apuesta['cuota']).replace(',', '.')
        
        # Ahora sí, Python lo entiende perfecto
        cuota_total *= float(valor_str)
    ganancia = round(monto * cuota_total, 2)
    cur.execute("INSERT INTO tickets (id_usuario, monto_total, ganancia_posible, estado, fecha) VALUES (%s, %s, %s, 'pendiente', NOW())", (id_usuario, monto, ganancia))
    id_ticket = cur.lastrowid
    for apuesta in lista_apuestas:
        cur.execute("INSERT INTO detalles_apuesta (id_ticket, id_partido, seleccion, cuota_momento) VALUES (%s, %s, %s, %s)", (id_ticket, apuesta['idPartido'], apuesta['seleccion'], apuesta['cuota']))
    cur.execute("UPDATE usuarios SET saldo = saldo - %s WHERE id_usuario = %s", (monto, id_usuario))
    mysql.connection.commit()
    session['saldo'] = saldo_actual - monto
    flash(f"✅ Apuesta realizada. Ticket #{id_ticket}. Ganancia: ${ganancia}")
    return redirect(url_for('panel'))

@app.route('/mis_apuestas')
def mis_apuestas():
    if 'id_usuario' not in session: return redirect(url_for('Index'))
    id_usuario = session['id_usuario']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tickets WHERE id_usuario = %s ORDER BY fecha DESC", (id_usuario,))
    tickets_data = list(cur.fetchall())
    if not tickets_data:
        return render_template('mis_apuestas.html', tickets=[], nombre=session['nombre'], saldo=session['saldo'])
    columnas_ticket = [d[0] for d in cur.description]
    mis_tickets = []
    for row in tickets_data:
        t = dict(zip(columnas_ticket, row))
        cur.execute("SELECT d.seleccion, d.cuota_momento, p.local, p.visitante, p.liga FROM detalles_apuesta d JOIN partidos p ON d.id_partido = p.id WHERE d.id_ticket = %s", (t['id_ticket'],))
        detalles_data = list(cur.fetchall())
        items = []
        if detalles_data:
            cols_det = [d[0] for d in cur.description]
            for d in detalles_data: items.append(dict(zip(cols_det, d)))
        t['lista_detalles'] = items
        mis_tickets.append(t)
    return render_template('mis_apuestas.html', tickets=mis_tickets, nombre=session['nombre'], saldo=session['saldo'])

@app.route('/admin')
def admin(): return render_template('admin.html')

@app.route('/admin/usuarios')
def admin_usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    columnas = [d[0] for d in cur.description]
    usuarios = [dict(zip(columnas, row)) for row in cur.fetchall()]
    return render_template('usuarios.html', usuarios=usuarios)
# ==========================================
#  ACCIÓN DE ELIMINAR (MODO NUCLEAR ☢️)
# ==========================================
@app.route('/delete_user/<string:id>')
def delete_user(id):
    # 1. Seguridad: Verificar si es admin
    if 'rol' not in session or session['rol'] != 'admin':
        flash("⛔ Acceso denegado")
        return redirect(url_for('panel'))

    cur = mysql.connection.cursor()
    
    try:
        # Recuperar nombre para borrar foto
        cur.execute("SELECT nombre FROM usuarios WHERE id_usuario = %s", (id,))
        dato = cur.fetchone()
        nombre_usuario = dato[0] if dato else None


        
        # 1. Borrar Detalles de Apuestas (Nietos)
        cur.execute("""
            DELETE FROM detalles_apuesta 
            WHERE id_ticket IN (SELECT id_ticket FROM tickets WHERE id_usuario = %s)
        """, (id,))
        
        # 2. Borrar Tickets
        cur.execute("DELETE FROM tickets WHERE id_usuario = %s", (id,))
        
        # 3. Borrar Recargas
        cur.execute("DELETE FROM recarga WHERE id_usuario = %s", (id,))
        
        # 4. Borrar Datos Biométricos
        if nombre_usuario:
            cur.execute("DELETE FROM datos_biometricos WHERE nombre_usuario = %s", (nombre_usuario,))
        
        # 5.  Borrar Usuario
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        
        mysql.connection.commit()
        flash('✅ Usuario eliminado exitosamente')
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error crítico: {e}")
        flash(f'❌ Error técnico: {e}')

    return redirect(url_for('admin_usuarios'))

    # ==========================================
#  CREAR USUARIO DESDE ADMIN
# ==========================================
@app.route('/admin/crear_usuario', methods=['POST'])
def admin_crear_usuario():
    
    if 'rol' not in session or session['rol'] != 'admin':
        return redirect(url_for('panel'))

    if request.method == 'POST':
    
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contraseña = request.form['contraseña']
        saldo = request.form['saldo'] 

    
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (nombre, apellido, email, contraseña, saldo, fecha_registro) VALUES (%s, %s, %s, %s, %s, NOW())", (nombre, apellido, email, contraseña, saldo))
        mysql.connection.commit()
        
        flash("✅ Usuario creado exitosamente desde el panel.")
        
    return redirect(url_for('admin_usuarios'))

    # ==========================================
#  GESTIÓN DE PARTIDOS (ADMIN)
# ==========================================

@app.route('/admin/partidos')
def admin_partidos():
    if 'rol' not in session or session['rol'] != 'admin':
        return redirect(url_for('panel'))

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM partidos ORDER BY id DESC")
        columnas = [d[0] for d in cur.description]
        partidos = [dict(zip(columnas, row)) for row in cur.fetchall()]
    finally:
        cur.close()
    
    return render_template('partidos.html', partidos=partidos)

@app.route('/admin/crear_partido', methods=['POST'])
def admin_crear_partido():
    if 'rol' not in session or session['rol'] != 'admin': 
        return redirect(url_for('panel'))

    if request.method == 'POST':
        liga = request.form['liga']
        local = request.form['local']
        visitante = request.form['visitante']
        tiempo = request.form['tiempo'] 
        c1 = request.form['cuota_1']
        cx = request.form['cuota_x']
        c2 = request.form['cuota_2']
        
        img_local = "none" 
        img_visitante = "none"

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO partidos (liga, local, visitante, tiempo, cuota_1, cuota_x, cuota_2, img_local, img_visitante, categoria)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'futbol')
            """, (liga, local, visitante, tiempo, c1, cx, c2, img_local, img_visitante))
            mysql.connection.commit()
            flash("✅ Partido creado correctamente")
        finally:
            cur.close()
        
    return redirect(url_for('admin_partidos'))

@app.route('/eliminar_partido/<string:id>')
def eliminar_partido(id):
    if 'rol' not in session or session['rol'] != 'admin': return redirect(url_for('panel'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM partidos WHERE id = %s", (id,))
    mysql.connection.commit()
    flash("🗑️ Partido eliminado")
    return redirect(url_for('admin_partidos'))

# ==========================================
#  EDITAR USUARIO (Faltaba esto)
# ==========================================
@app.route('/edit_user/<string:id>')
def edit_user(id):
    # 1. Seguridad: Solo admin entra aquí
    if 'rol' not in session or session['rol'] != 'admin':
        return redirect(url_for('panel'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
    data = cur.fetchone()
    
    # Convertimos los datos a diccionario para usarlos fácil en el HTML
    if data:
        columnas = [d[0] for d in cur.description]
        usuario = dict(zip(columnas, data))
        return render_template('editar_usuario.html', usuario=usuario)
    else:
        flash("❌ Usuario no encontrado")
        return redirect(url_for('admin_usuarios'))

@app.route('/update_user/<string:id>', methods=['POST'])
def update_user(id):
    if 'rol' not in session or session['rol'] != 'admin':
        return redirect(url_for('panel'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        saldo = request.form['saldo']
        rol = request.form['rol'] # Importante poder cambiar roles (admin/user)
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE usuarios
            SET nombre = %s, apellido = %s, email = %s, saldo = %s, rol = %s
            WHERE id_usuario = %s
        """, (nombre, apellido, email, saldo, rol, id))
        mysql.connection.commit()
        
        flash("✅ Usuario actualizado exitosamente")
        return redirect(url_for('admin_usuarios'))
    
    # ==========================================
#  EDITAR USUARIO (Ruta conectada al Modal)
# ==========================================
@app.route('/editar_usuario/<string:id>', methods=['POST'])
def editar_usuario(id):
    # 1. Seguridad: Solo admin puede hacer esto
    if 'rol' not in session or session['rol'] != 'admin':
        return redirect(url_for('panel'))

    if request.method == 'POST':
        # 2. Recibimos los datos EXACTOS de tu formulario HTML
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contraseña = request.form['contraseña']  # ¡Aquí está la contraseña que faltaba!
        saldo = request.form['saldo']
        
        # 3. Guardamos en la Base de Datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE usuarios
            SET nombre = %s, apellido = %s, email = %s, contraseña = %s, saldo = %s
            WHERE id_usuario = %s
        """, (nombre, apellido, email, contraseña, saldo, id))
        mysql.connection.commit()
        
        flash("✅ Usuario actualizado correctamente")
        return redirect(url_for('admin_usuarios'))
    
    # Agrega esto para que no se cuelgue buscando el icono
@app.route('/favicon.ico')
def favicon():
    return "", 204

if __name__ == '__main__':
    app.run(port=3000, debug=False, threaded=True)
