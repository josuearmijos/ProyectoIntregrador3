
from app import app
from flask import render_template, request, flash, redirect, url_for, session

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *
from controllers.funciones_home import *
PATH_URL_LOGIN = "/public/login"


@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/mi-perfil/<int:id>', methods=['GET'])
def perfil(id):
    if 'conectado' in session:
        usuario = info_perfil_session(id)
        print("Datos del usuario:", usuario)  # Verificar los datos
        return render_template(
            'public/perfil/perfil.html',
            info_perfil_session=usuario,
            dataLogin=dataLoginSesion(),
            areas=lista_areasBD(),
            roles=lista_rolesBD()
        )
    else:
        return redirect(url_for('login'))


# Crear cuenta de usuario
@app.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html',dataLogin = dataLoginSesion(),areas=lista_areasBD(), roles=lista_rolesBD())


# Recuperar cuenta de usuario
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@app.route('/saved-register', methods=['POST'])
def cpanelRegisterUserBD():
    if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:
        cedula = request.form['cedula']
        name = request.form['name']
        surname = request.form['surname']
        id_area = request.form['selectArea']
        id_rol = request.form['selectRol']
        pass_user = request.form['pass_user']

        resultData = recibeInsertRegisterUser(
            cedula, name, surname, id_area, id_rol, pass_user)
        if (resultData != 0):
            flash('la cuenta fue creada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            return redirect(url_for('inicio'))
    else:
        flash('el método HTTP es incorrecto', 'error')
        return redirect(url_for('inicio'))


# Actualizar datos de mi perfil
@app.route('/actualizarPerfil/<int:id>', methods=['POST'])
def actualizarPerfil(id):
    if 'conectado' not in session:
        flash('Debes iniciar sesión para realizar esta acción', 'error')
        return redirect(url_for('login'))

    # Obtener el usuario por ID
    usuario = obtenerUsuarioPorId(id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('perfil', id=id))

    # Validar la clave actual
    clave_actual = request.form.get('pass_actual')
    if not clave_actual or not usuario.get('password'):
        flash('Clave actual no proporcionada o no encontrada', 'error')
        return redirect(url_for('perfil', id=id))

    if not check_password_hash(usuario['password'], clave_actual):
        flash('La clave actual es incorrecta', 'error')
        return redirect(url_for('perfil', id=id))

    # Actualizar la nueva clave si se proporciona
    nueva_clave = request.form.get('new_pass_user')
    if nueva_clave:
        nueva_clave_hashed = generate_password_hash(nueva_clave)
        actualizarClaveUsuario(id, nueva_clave_hashed)

    flash('Perfil actualizado con éxito', 'success')
    return redirect(url_for('perfil', id=id))



# Validar sesión
@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:

            cedula = str(request.form['cedula'])
            pass_user = str(request.form['pass_user'])
            conexion_MySQLdb = connectionBD()
            print(conexion_MySQLdb)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM usuarios WHERE cedula = %s", [cedula])
            account = cursor.fetchone()

            if account:
                if check_password_hash(account['password'], pass_user):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas
                    session['conectado'] = True
                    session['id'] = account['id_usuario']
                    session['name'] = account['nombre_usuario']
                    session['cedula'] = account['cedula']
                    session['rol'] = account['id_rol'] if 'id_rol' in account else 0

                    flash('la sesión fue correcta.', 'success')
                    return redirect(url_for('inicio'))
                else:
                    # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
                    flash('datos incorrectos por favor revise.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('el usuario no existe, por favor verifique.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/closed-session',  methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email', None)
            flash('tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('recuerde debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
