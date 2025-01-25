from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *

@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html', areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
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

@app.route('/editar-departamento/<int:id_departamento>')
def editar_departamento(id_departamento):
    # Lógica para editar el departamento
    return f"Editar departamento {id_departamento}"

@app.route('/eliminar-departamento/<int:id_departamento>')
def eliminar_departamento(id_departamento):
    # Lógica para eliminar el departamento
    return f"Eliminar departamento {id_departamento}"



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
        return render_template('public/perfil/reportes.html',  reportes=dataReportes(),lastAccess=lastAccessBD(userData.get('cedula')), dataLogin=dataLoginSesion())

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


#CREAR Tarjeta
@app.route('/añadir-tarjeta', methods=['GET','POST'])
def añadirTarjeta():
    if request.method == 'POST':
        card_name = request.form['nombre_tarjeta']  # Asumiendo que 'nombre_area' es el nombre del campo en el formulario
        resultado_insert = añadirTarjeta(card_name)
        if resultado_insert:
            # Éxito al guardar el área
            flash('La tarjeta fue añadida correctamente', 'success')
            return redirect(url_for('lista_tarjetas'))
            
        else:
            # Manejar error al guardar el área
            return "Hubo un error al guardar la tarjeta."
    return render_template('public/usuarios/lista_tarjetas')

@app.route('/borrar-tarjeta/<string:id_tarjeta>/', methods=['GET'])
def borrarTarjeta(id_tarjeta):
    resp = eliminarTarjeta(id_tarjeta)
    if resp:
        flash('La tarjeta fue eliminada correctamente', 'success')
        return redirect(url_for('lista_tarjetas'))
    else:
        flash('No se pudo eliminar la tarjeta.', 'error')
        return redirect(url_for('lista_tarjetas'))


    