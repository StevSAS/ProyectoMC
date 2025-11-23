import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)

# --- CONFIGURACIÓN MYSQL (XAMPP) ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Stev'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'apuesta'
mysql = MySQL(app)

app.secret_key = "mysecretkey"

# ==========================================
# RUTAS DE ACCESO
# ==========================================

@app.route('/')
def Index():
    if 'id_usuario' in session:
        return redirect(url_for('panel'))
    return render_template('principal.html')

@app.route('/registrarse')
def registrarse():
    return render_template('registro.html')

@app.route('/agregar_usuario', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        # Guardamos la contraseña tal cual (Texto plano)
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, email, contraseña, saldo, fecha_registro) 
            VALUES (%s, %s, %s, %s, 0, NOW())
        """, (nombre, apellido, email, contraseña))
        mysql.connection.commit()
        flash("Usuario registrado correctamente")
        return redirect(url_for('Index'))

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        # Verificamos usuario y contraseña directamente
        cur.execute("SELECT id_usuario, nombre, saldo FROM usuarios WHERE email=%s AND contraseña=%s", (email, contraseña))
        user = cur.fetchone()

        if user:
            session['id_usuario'] = user[0]
            session['nombre'] = user[1]
            session['saldo'] = float(user[2])
            return redirect(url_for('panel'))
        else:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for('Index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Index'))

# ==========================================
# PANEL PRINCIPAL
# ==========================================

@app.route('/panel')
def panel():
    if 'id_usuario' not in session:
        return redirect(url_for('Index'))

    id_usuario = session['id_usuario']
    cur = mysql.connection.cursor()

    # 1. Saldo Actualizado
    cur.execute("SELECT saldo FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    res = cur.fetchone()
    if res:
        session['saldo'] = float(res[0])

    # 2. Partidos desde la Base de Datos
    cur.execute("SELECT * FROM partidos")
    columnas = [d[0] for d in cur.description]
    partidos_db = [dict(zip(columnas, row)) for row in cur.fetchall()]

    # 3. Formato de cuotas
    lista_final = []
    for p in partidos_db:
        p['cuotas'] = {
            '1': p['cuota_1'],
            'X': p['cuota_x'],
            '2': p['cuota_2']
        }
        lista_final.append(p)

    return render_template("panel.html", 
                           partidos=lista_final, 
                           saldo=session['saldo'], 
                           nombre=session['nombre'])

# ==========================================
# RECARGAS
# ==========================================

@app.route('/recargar')
def recargar():
    if 'id_usuario' not in session:
        return redirect(url_for('login'))
    return render_template('recargar.html')

@app.route('/guardar_recarga', methods=['POST'])
def guardar_recarga():
    if 'id_usuario' not in session:
        return redirect(url_for('login'))

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

# ==========================================
# PROCESAR APUESTA
# ==========================================

@app.route('/procesar_apuesta', methods=['POST'])
def procesar_apuesta():
    if 'id_usuario' not in session:
        return redirect(url_for('Index'))

    monto = float(request.form.get('monto_apuesta'))
    id_usuario = session['id_usuario']
    datos_json = request.form.get('datos_apuestas')
    lista_apuestas = json.loads(datos_json)
    
    cur = mysql.connection.cursor()
    
    # 1. Verificar Saldo
    cur.execute("SELECT saldo FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    saldo_actual = float(cur.fetchone()[0])

    if monto > saldo_actual:
        flash("❌ Saldo insuficiente")
        return redirect(url_for('panel'))

    # 2. Calcular Ganancia
    cuota_total = 1
    for apuesta in lista_apuestas:
        cuota_total *= float(apuesta['cuota'])
    ganancia = round(monto * cuota_total, 2)

    # 3. Guardar Ticket
    cur.execute("""
        INSERT INTO tickets (id_usuario, monto_total, ganancia_posible, estado, fecha)
        VALUES (%s, %s, %s, 'pendiente', NOW())
    """, (id_usuario, monto, ganancia))
    id_ticket = cur.lastrowid

    # 4. Guardar Detalles
    for apuesta in lista_apuestas:
        cur.execute("""
            INSERT INTO detalles_apuesta (id_ticket, id_partido, seleccion, cuota_momento)
            VALUES (%s, %s, %s, %s)
        """, (id_ticket, apuesta['idPartido'], apuesta['seleccion'], apuesta['cuota']))

    # 5. Descontar dinero
    cur.execute("UPDATE usuarios SET saldo = saldo - %s WHERE id_usuario = %s", (monto, id_usuario))
    mysql.connection.commit()
    
    session['saldo'] = saldo_actual - monto
    flash(f"✅ Apuesta realizada. Ticket #{id_ticket}. Ganancia: ${ganancia}")
    
    return redirect(url_for('panel'))

# ==========================================
# HISTORIAL DE APUESTAS
# ==========================================

@app.route('/mis_apuestas')
def mis_apuestas():
    if 'id_usuario' not in session:
        return redirect(url_for('Index'))

    id_usuario = session['id_usuario']
    cur = mysql.connection.cursor()

    # 1. Tickets
    cur.execute("SELECT * FROM tickets WHERE id_usuario = %s ORDER BY fecha DESC", (id_usuario,))
    tickets_data = list(cur.fetchall())

    if not tickets_data:
        return render_template('mis_apuestas.html', tickets=[], nombre=session['nombre'], saldo=session['saldo'])

    columnas_ticket = [d[0] for d in cur.description]
    mis_tickets = []

    for row in tickets_data:
        t = dict(zip(columnas_ticket, row))
        
        # 2. Detalles
        cur.execute("""
            SELECT d.seleccion, d.cuota_momento, p.local, p.visitante, p.liga 
            FROM detalles_apuesta d
            JOIN partidos p ON d.id_partido = p.id
            WHERE d.id_ticket = %s
        """, (t['id_ticket'],))
        
        detalles_data = list(cur.fetchall())
        
        items = []
        if detalles_data:
            cols_det = [d[0] for d in cur.description]
            for d in detalles_data:
                items.append(dict(zip(cols_det, d)))
        
        # Usamos lista_detalles para evitar el error con items()
        t['lista_detalles'] = items
        mis_tickets.append(t)

    return render_template('mis_apuestas.html', 
                           tickets=mis_tickets, 
                           nombre=session['nombre'], 
                           saldo=session['saldo'])

# ==========================================
# ADMIN
# ==========================================

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin/usuarios')
def admin_usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario, nombre, apellido, email, contraseña, fecha_registro, saldo FROM usuarios")
    columnas = [desc[0] for desc in cur.description]
    usuarios = [dict(zip(columnas, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/admin/partidos')
def admin_partidos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, categoria, liga, local, visitante, tiempo, cuota_1, cuota_x, cuota_2 FROM partidos")
    columnas = [desc[0] for desc in cur.description]
    partidos = [dict(zip(columnas, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('partidos.html', partidos=partidos)


if __name__ == '__main__':
    app.run(port=3000, debug=True)