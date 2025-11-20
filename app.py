from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)

# mysql conexion
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Stev'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'apuesta'
mysql = MySQL(app)

# configuracion
app.secret_key = "mysecretkey"

@app.route('/')
def Index():
    return render_template('principal.html')


# ------------------- REGISTRO ---------------------
@app.route('/agregar_usuario', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuarios (nombre, apellido, email, contraseña, saldo)
            VALUES (%s, %s, %s, %s, 0)
        """, (nombre, apellido, email, contraseña))

        mysql.connection.commit()
        flash("Usuario registrado correctamente")
        return redirect(url_for('Index'))


# ------------------- LOGIN ------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_usuario, nombre, saldo 
            FROM usuarios 
            WHERE email=%s AND contraseña=%s
        """, (email, contraseña))

        user = cur.fetchone()

        if user:
            session['id_usuario'] = user[0]
            session['nombre'] = user[1]
            session['saldo'] = user[2]
            return redirect(url_for('panel'))
        else:
            return "Usuario o contraseña incorrectos"

    return render_template('login.html')


# ------------------- PANEL ------------------------
@app.route('/panel')
def panel():
    if 'id_usuario' not in session:
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']
    cur = mysql.connection.cursor()

    # Obtener saldo actualizado
    cur.execute("SELECT saldo, nombre FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    usuario = cur.fetchone()

    # Obtener historial de recargas
    cur.execute("""
        SELECT monto, metodo, fecha 
        FROM recarga 
        WHERE id_usuario=%s 
        ORDER BY fecha DESC
    """, (id_usuario,))
    recargas = cur.fetchall()

    return render_template("panel.html",
                           saldo=usuario[0],
                           usuario={"nombre": usuario[1]},
                           recargas=recargas)


# ------------------- RECARGA ------------------------
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

    # Insertar recarga
    cur.execute("""
        INSERT INTO recarga (id_usuario, monto, metodo, fecha)
        VALUES (%s, %s, %s, NOW())
    """, (id_usuario, monto, metodo))

    # Actualizar saldo
    cur.execute("""
        UPDATE usuarios 
        SET saldo = saldo + %s
        WHERE id_usuario = %s
    """, (monto, id_usuario))

    mysql.connection.commit()

    # --- SOLUCIÓN ---
    session['saldo'] = float(session['saldo']) + float(monto)

    flash("Recarga realizada. Saldo actualizado.")
    return redirect(url_for('panel'))


@app.route('/registrarse')
def registrarse():
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)
    


