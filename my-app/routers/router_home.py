from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error
from controllers.funciones_home import editarArea, eliminarArea


# Importando cenexión a BD
from controllers.funciones_home import *

@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        try:
            # Obtener lista de áreas y departamentos
            conexion = connectionBD()
            with conexion.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM departamentos"
                cursor.execute(query)
                departamentos = cursor.fetchall()

            conexion.close()

            return render_template('public/usuarios/lista_areas.html', 
                                   areas=lista_areasBD(), 
                                   departamentos=departamentos, 
                                   dataLogin=dataLoginSesion())
        except Exception as e:
            print(f"Error al cargar las áreas y departamentos: {e}")
            flash('Hubo un error al cargar las áreas y departamentos.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/departamentos')
def departamentos():
    try:
        conexion = connectionBD()
        with conexion.cursor(dictionary=True) as cursor:
            query = "SELECT id_departamento, nombre_departamento, id_propietario FROM departamentos"
            cursor.execute(query)
            departamentos = cursor.fetchall()
        conexion.close()

        # Simulación de sesión
        dataLogin = {'id': 1, 'rol': 1, 'cedula': '1234567890'}

        return render_template('public/usuarios/departamentos.html', departamentos=departamentos, dataLogin=dataLogin)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('public/usuarios/departamentos.html', departamentos=[], dataLogin={})



@app.route('/crear-departamento', methods=['POST'])
def crear_departamento():
    try:
        # Capturar datos del formulario
        nombre_departamento = request.form['nombre_departamento']
        id_propietario = request.form['id_propietario_departamento']
        id_edificio = request.form['id_edificio']  # Capturar el ID del edificio

        # Conexión a la base de datos
        conexion = connectionBD()
        with conexion.cursor() as cursor:
            query = """
                INSERT INTO departamentos (nombre_departamento, id_propietario, id_edificio)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (nombre_departamento, id_propietario, id_edificio))
            conexion.commit()

        conexion.close()
        flash('Departamento creado correctamente.', 'success')
        return redirect(url_for('lista_areas'))  # Redirigir a la lista de áreas
    except Exception as e:
        print(f"Error al crear el departamento: {e}")
        flash('Hubo un error al crear el departamento.', 'error')
        return redirect(url_for('lista_areas'))  # Redirigir a la lista de áreas

#editar  y eliminar areas
@app.route('/eliminar-area/<int:id_area>', methods=['POST'])
def eliminar_area(id_area):
    resp = eliminarArea(id_area)
    if resp['status'] == 'success':
        flash(resp['message'], 'success')
    else:
        flash(resp['message'], 'error')
    return redirect(url_for('lista_areas'))
@app.route('/editar-area/<int:id_area>', methods=['POST'])
def editar_area(id_area):
    nuevo_nombre = request.form.get('nombre_area')
    resp = editarArea(id_area, nuevo_nombre)
    if resp['status'] == 'success':
        flash(resp['message'], 'success')
    else:
        flash(resp['message'], 'error')
    return redirect(url_for('lista_areas'))

# Ruta para el control de luces
@app.route('/control_luces', methods=['GET', 'POST'])
def control_luces():
    try:
        conexion = connectionBD()
        
        # Simulación de sesión
        if 'conectado' in session:
         dataLogin = dataLoginSesion()
        else:
         flash('Debes iniciar sesión primero', 'error')
         return redirect(url_for('inicio'))

        if request.method == 'POST':
            # Obtener datos del formulario
            departamento_id = request.form.get('departamento')
            color = request.form.get('color')

            # Actualizar color en la base de datos para el departamento del propietario
            with conexion.cursor(dictionary=True) as cursor:
                query = """
                UPDATE configuracion_luces
                SET color = %s
                WHERE id_departamento = %s AND id_departamento IN (
                    SELECT id_departamento
                    FROM departamentos
                    WHERE id_propietario = %s
                )
                """
                cursor.execute(query, (color, departamento_id, dataLogin['id']))
                conexion.commit()

        # Obtener departamentos del usuario propietario
        with conexion.cursor(dictionary=True) as cursor:
            query = """
            SELECT d.id_departamento, d.nombre_departamento, cl.color
            FROM departamentos d
            LEFT JOIN configuracion_luces cl ON d.id_departamento = cl.id_departamento
            WHERE d.id_propietario = %s
            """
            cursor.execute(query, (dataLogin['id'],))
            departamentos = cursor.fetchall()

        conexion.close()

        return render_template('public/usuarios/control_luces.html', departamentos=departamentos, dataLogin=dataLogin)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('public/usuarios/control_luces.html', departamentos=[], dataLogin={})



@app.route('/editar-departamento/<int:id_departamento>', methods=['GET', 'POST'])
def editar_departamento(id_departamento):
    if request.method == 'POST':
        # Recibir datos del formulario
        nombre_departamento = request.form.get('name')
        id_propietario = request.form.get('id_propietario')

        try:
            # Conectar a la base de datos
            conexion = connectionBD()
            with conexion.cursor() as cursor:
                # Actualizar los datos del departamento
                query = """
                UPDATE departamentos 
                SET nombre_departamento = %s, id_propietario = %s 
                WHERE id_departamento = %s
                """
                cursor.execute(query, (nombre_departamento, id_propietario, id_departamento))
                conexion.commit()

            conexion.close()
            flash('Departamento actualizado correctamente.', 'success')
            return redirect(url_for('lista_areas'))
        except Exception as e:
            print(f"Error al actualizar el departamento: {e}")
            flash('Hubo un error al actualizar el departamento.', 'error')
            return redirect(url_for('editar_departamento', id_departamento=id_departamento))

    try:
        # Obtener datos del departamento y su edificio desde la base de datos
        conexion = connectionBD()
        with conexion.cursor(dictionary=True) as cursor:
            query = """
            SELECT d.*, e.nombre_edificio
            FROM departamentos d
            LEFT JOIN edificios e ON d.id_edificio = e.id_edificio
            WHERE d.id_departamento = %s
            """
            cursor.execute(query, (id_departamento,))
            departamento = cursor.fetchone()

        conexion.close()

        if not departamento:
            flash('El departamento no existe o no se encontró.', 'error')
            return redirect(url_for('lista_areas'))

        # Verificar si hay sesión activa
        if 'conectado' in session:
            dataLogin = {
                "id": session.get('id'),
                "name": session.get('name'),
                "cedula": session.get('cedula'),
                "rol": session.get('rol', 0)
            }
        else:
            flash('Debes iniciar sesión primero', 'error')
            return redirect(url_for('inicio'))

        # Renderizar la página de edición con datos del departamento y el edificio
        return render_template('public/usuarios/departamentos_editar.html', 
                               departamento=departamento, 
                               edificio=departamento.get('nombre_edificio', ''), 
                               dataLogin=dataLogin)
    except Exception as e:
        print(f"Error al cargar el departamento: {e}")
        flash('Hubo un error al cargar el departamento.', 'error')
        return redirect(url_for('lista_areas'))



@app.route('/eliminar-departamento/<int:id_departamento>', methods=['POST'])
def eliminar_departamento(id_departamento):
    try:
        conexion = connectionBD()
        with conexion.cursor() as cursor:
            # Verificar si el departamento existe antes de eliminarlo
            query_check = "SELECT * FROM departamentos WHERE id_departamento = %s"
            cursor.execute(query_check, (id_departamento,))
            departamento = cursor.fetchone()

            if not departamento:
                flash('El departamento no existe.', 'error')
                return redirect(url_for('lista_areas'))


            # Eliminar el departamento
            query = "DELETE FROM departamentos WHERE id_departamento = %s"
            cursor.execute(query, (id_departamento,))
            conexion.commit()

        conexion.close()
        flash('Departamento eliminado correctamente.', 'success')
    except Exception as e:
        print(f"Error al eliminar el departamento: {e}")
        flash('Hubo un error al eliminar el departamento.', 'error')

    return redirect(url_for('lista_areas'))



@app.route('/obtener-departamentos', methods=['GET'])
def obtener_departamentos():
    try:
        # Conectar a la base de datos
        conexion = connectionBD()
        with conexion.cursor(dictionary=True) as cursor:
            # Consulta para obtener los departamentos
            query = "SELECT id_departamento, nombre_departamento, id_propietario FROM departamentos"
            cursor.execute(query)
            departamentos = cursor.fetchall()

        conexion.close()

        # Devuelve los departamentos como JSON
        return {"departamentos": departamentos}, 200
    except Exception as e:
        print(f"Error al obtener los departamentos: {e}")
        return {"error": "No se pudieron obtener los departamentos"}, 500

# ruta para accesos xdxd
@app.route('/reporte-accesos', methods=['GET'])
def reporte_accesos():
    try:
        conexion = connectionBD()
        with conexion.cursor(dictionary=True) as cursor:
            # Consulta para obtener todos los accesos
            query = """
            SELECT 
                a.id_acceso, 
                u.cedula, 
                a.fecha, 
                t.codigo_hexadecimal AS clave
            FROM 
                Domus.accesos a
            INNER JOIN 
                Domus.usuarios u ON a.id_usuario = u.id_usuario
            INNER JOIN 
                Domus.tarjetas_rfid t ON a.id_tarjeta = t.id_tarjeta
            """
            cursor.execute(query)
            reportes = cursor.fetchall()
            query_last_access = """
            SELECT 
                a.fecha, 
                t.codigo_hexadecimal AS clave
            FROM 
                Domus.accesos a
            INNER JOIN 
                Domus.tarjetas_rfid t ON a.id_tarjeta = t.id_tarjeta
            ORDER BY a.fecha DESC
            LIMIT 1
            """
            cursor.execute(query_last_access)
            lastAccess = cursor.fetchone()
        
        conexion.close()

        # Simulación de sesión
        dataLogin = {'id': 1, 'rol': 1, 'cedula': '1234567890'}

        return render_template('public/perfil/reportes.html', reportes=reportes, lastAccess=lastAccess, dataLogin=dataLogin)
    except Exception as e:
        print(f"Error al obtener el reporte: {e}")
        return render_template('public/perfil/reportes.html', reportes=[], lastAccess={}, dataLogin={})


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html',  resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles = lista_rolesBD())
    else:
        return redirect(url_for('inicioCpanel'))

#Ruta especificada para eliminar un usuario
@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    
@app.route('/borrar-area/<string:id_area>/', methods=['GET'])
def borrarArea(id_area):
    resp = eliminarArea(id_area)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_areas'))
    else:
        flash('Hay usuarios que pertenecen a esta área', 'error')
        return redirect(url_for('lista_areas'))


@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/perfil/reportes.html',
                               reportes=dataReportesPorUsuario(userData.get('id')),
                               lastAccess=lastAccessBD(userData.get('cedula')),
                               dataLogin=userData)
    else:
        flash('Debe iniciar sesión para ver esta página.', 'error')
        return redirect(url_for('inicio'))

@app.route("/interfaz-clave", methods=['GET','POST'])
def claves():
    return render_template('public/usuarios/generar_clave.html', dataLogin=dataLoginSesion())
    
@app.route('/generar-y-guardar-clave/<string:id>', methods=['GET','POST'])
def generar_clave(id):
    print(id)
    clave_generada = crearClave()  # Llama a la función para generar la clave
    guardarClaveAuditoria(clave_generada,id)
    return clave_generada
#CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if request.method == 'POST':
        area_name = request.form['nombre_area']  # Asumiendo que 'nombre_area' es el nombre del campo en el formulario
        resultado_insert = guardarArea(area_name)
        if resultado_insert:
            # Éxito al guardar el área
            flash('El Area fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
            
        else:
            # Manejar error al guardar el área
            return "Hubo un error al guardar el área."
    return render_template('public/usuarios/lista_areas')

##ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if request.method == 'POST':
        nombre_area = request.form['nombre_area']  # Asumiendo que 'nuevo_nombre' es el nombre del campo en el formulario
        id_area = request.form['id_area']
        resultado_update = actualizarArea(id_area, nombre_area)
        if resultado_update:
# Éxito al actualizar el área
            flash('El actualizar fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            # Manejar error al actualizar el área
            return "Hubo un error al actualizar el área."

    return redirect(url_for('lista_areas'))

#Select tarjetas
@app.route('/lista-de-tarjetas', methods=['GET'])
def lista_tarjetas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_tarjetas.html', tarjetas=lista_tarjetasBD(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/añadir-tarjeta', methods=['GET', 'POST'])
def añadirTarjeta():
    if request.method == 'POST':
        card_name = request.form['nombre_tarjeta']  
        resultado_insert = agregarTarjeta(card_name,)
        if resultado_insert:
            flash('La tarjeta fue añadida correctamente', 'success')
            return redirect(url_for('lista_tarjetas'))
        else:
            return "Hubo un error al guardar la tarjeta."


@app.route('/borrar-tarjeta/<string:id_tarjeta>/', methods=['GET'])
def borrarTarjeta(id_tarjeta):
    resp = eliminarTarjeta(id_tarjeta)
    if resp > 0:  # Se cambia la condición para asegurar que solo muestra error si ocurre una falla real
        flash('La tarjeta fue eliminada correctamente', 'success')
    else:
        flash('No se encontró la tarjeta para eliminar.', 'error')
    return redirect(url_for('lista_tarjetas'))

#Activa inactiva tarjeta
@app.route('/cambiar-estado-tarjeta/<int:id_tarjeta>', methods=['GET'])
def cambiarEstadoTarjeta(id_tarjeta):
    if cambiar_estado_tarjeta(id_tarjeta):
        return redirect(url_for('lista_tarjetas'))
    else:
        return "Error al cambiar el estado de la tarjeta", 500

@app.route('/historial-sensores', methods=['GET'])
def historial_sensores():
    if 'conectado' in session:
        return render_template('public/usuarios/historial_sensores.html', historial_sensores=obtener_registros_sensores(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/edificios', methods=['GET'])
def edificios():
    if 'conectado' in session:
        return render_template('public/usuarios/edificios.html', edificios=obtener_edificios(), dataLogin=dataLoginSesion())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


