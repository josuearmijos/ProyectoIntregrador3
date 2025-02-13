
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
from app import app  # Asegúrate de importar la instancia de Flask correctamente
from flask import jsonify

import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import sys
import datetime
import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio


import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file, session

def accesosReporte():
    if session['rol'] == 1 :
        try:
            with connectionBD() as conexion_MYSQLdb:
                with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                    querySQL = ("""
                        SELECT a.id_acceso, u.cedula, a.fecha, r.nombre_area, a.clave 
                        FROM accesos a 
                        JOIN usuarios u 
                        JOIN area r
                        WHERE u.id_area = r.id_area AND u.id_usuario = a.id_usuario
                        ORDER BY u.cedula, a.fecha DESC
                                """) 
                    cursor.execute(querySQL)
                    accesosBD=cursor.fetchall()
                return accesosBD
        except Exception as e:
            print(
                f"Error en la función accesosReporte: {e}")
            return None
    else:
        cedula = session['cedula']
        try:
            with connectionBD() as conexion_MYSQLdb:
                with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                    querySQL = ("""
                        SELECT 
                            a.id_acceso, 
                            u.cedula, 
                            a.fecha,
                            r.nombre_area, 
                            a.clave 
                            FROM accesos a 
                            JOIN usuarios u JOIN area r 
                            WHERE u.id_usuario = a.id_usuario AND u.id_area = r.id_area AND u.cedula = %s
                            ORDER BY u.cedula, a.fecha DESC
                                """) 
                    cursor.execute(querySQL,(cedula,))
                    accesosBD=cursor.fetchall()
                return accesosBD
        except Exception as e:
            print(
                f"Errro en la función accesosReporte: {e}")
            return None


def generarReporteExcel():
    dataAccesos = accesosReporte()
    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("ID", "CEDULA", "FECHA", "ÁREA", "CLAVE GENERADA")

    hoja.append(cabeceraExcel)

    # Agregar los registros a la hoja
    for registro in dataAccesos:
        id_acceso = registro['id_acceso']
        cedula = registro['cedula']
        fecha = registro['fecha']
        area = registro['nombre_area']
        clave = registro['clave']

        # Agregar los valores a la hoja
        hoja.append((id_acceso, cedula, fecha,area, clave))

    fecha_actual = datetime.datetime.now()
    archivoExcel = f"Reporte_accesos_{session['cedula']}_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "../static/downloads-excel"
    ruta_descarga = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        # Dando permisos a la carpeta
        os.chmod(ruta_descarga, 0o755)

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    # Enviar el archivo como respuesta HTTP
    return send_file(ruta_archivo, as_attachment=True)

def buscarAreaBD(search):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            a.id_area,
                            a.nombre_area
                        FROM area AS a
                        WHERE a.nombre_area LIKE %s 
                        ORDER BY a.id_area DESC
                    """)
                search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoBD: {e}")
        return []


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_usuario, cedula, nombre_usuario, apellido_usuario, id_area, id_rol, fecha_registro FROM usuarios"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []

def lista_areasBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_area, nombre_area FROM area"
                cursor.execute(querySQL,)
                areasBD = cursor.fetchall()
        return areasBD
    except Exception as e:
        print(f"Error en lista_areas : {e}")
        return []

# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM usuarios WHERE id_usuario=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []    

def eliminarArea(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM area WHERE id_area=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarArea : {e}")
        return []
    
def dataReportes():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT a.id_acceso, u.cedula, a.fecha, r.nombre_area, a.clave 
                FROM accesos a 
                JOIN usuarios u 
                JOIN area r
                WHERE u.id_area = r.id_area AND u.id_usuario = a.id_usuario
                ORDER BY u.cedula, a.fecha DESC
                """
                cursor.execute(querySQL)
                reportes = cursor.fetchall()
        return reportes
    except Exception as e:
        print(f"Error en listaAccesos : {e}")
        return []
def dataReportesPorUsuario(id_usuario):
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT a.id_acceso, u.cedula, a.fecha, r.nombre_area, a.clave 
                FROM accesos a 
                JOIN usuarios u ON u.id_usuario = a.id_usuario
                JOIN area r ON u.id_area = r.id_area
                WHERE u.id_usuario = %s
                ORDER BY a.fecha DESC
                """
                cursor.execute(querySQL, (id_usuario,))
                reportes = cursor.fetchall()
        return reportes
    except Exception as e:
        print(f"Error en listaAccesos : {e}")
        return []

def lastAccessBD(id):
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT a.id_acceso, u.cedula, a.fecha, a.clave FROM accesos a JOIN usuarios u WHERE u.id_usuario = a.id_usuario AND u.cedula=%s ORDER BY a.fecha DESC LIMIT 1"
                cursor.execute(querySQL,(id,))
                reportes = cursor.fetchone()
                print(reportes)
        return reportes
    except Exception as e:
        print(f"Error en lastAcceso : {e}")
        return []
import random
import string
def crearClave():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y dígitos
    longitud = 6  # Longitud de la clave

    clave = ''.join(random.choice(caracteres) for _ in range(longitud))
    print("La clave generada es:", clave)
    return clave
##GUARDAR CLAVES GENERADAS EN AUDITORIA
def guardarClaveAuditoria(clave_audi,id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = "INSERT INTO accesos (fecha, clave, id_usuario) VALUES (NOW(),%s,%s)"
                    valores = (clave_audi,id)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error en crear Clave: {str(e)}'
    

def obtenerUsuarioPorId(id):
    connection = connectionBD()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE id_usuario = %s"  # Cambié 'id' por 'id_usuario'
    cursor.execute(query, (id,))
    usuario = cursor.fetchone()
    connection.close()
    return usuario

def actualizarClaveUsuario(id, nueva_clave_hashed):
    connection = connectionBD()
    cursor = connection.cursor()
    query = "UPDATE usuarios SET password = %s WHERE id_usuario = %s"  # Cambié 'id' por 'id_usuario'
    cursor.execute(query, (nueva_clave_hashed, id))
    connection.commit()
    connection.close()

 #funciones area
def editarArea(id, nuevo_nombre):
    try:
        conexion = connectionBD()
        with conexion.cursor() as cursor:
            query = "UPDATE area SET nombre_area = %s WHERE id_area = %s"
            cursor.execute(query, (nuevo_nombre, id))
            conexion.commit()
        conexion.close()
        return {"status": "success", "message": "Área actualizada correctamente."}
    except Exception as e:
        print(f"Error en editarArea: {e}")
        return {"status": "error", "message": "Error al actualizar el área."}
def eliminarArea(id):
    try:
        conexion = connectionBD()
        with conexion.cursor() as cursor:
            query = "DELETE FROM area WHERE id_area = %s"
            cursor.execute(query, (id,))
            conexion.commit()
        conexion.close()
        return {"status": "success", "message": "Área eliminada correctamente."}
    except Exception as e:
        print(f"Error en eliminarArea: {e}")
        return {"status": "error", "message": "Error al eliminar el área."}
  
def lista_rolesBD():
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM rol"
                cursor.execute(querySQL)
                roles = cursor.fetchall()
                return roles
    except Exception as e:
        print(f"Error en select roles : {e}")
        return []
##CREAR AREA
def guardarArea(area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                    sql = "INSERT INTO area (nombre_area) VALUES (%s)"
                    valores = (area_name,)
                    mycursor.execute(sql, valores)
                    conexion_MySQLdb.commit()
                    resultado_insert = mycursor.rowcount
                    return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error en crear Area: {str(e)}' 

##CREAR DEPARTAMENTO 
def guardarDepartamento(departamento_name, id_propietario):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = "INSERT INTO departamento (nombre_departamento, id_propietario) VALUES (%s, %s)"
                valores = (departamento_name, id_propietario)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_insert = mycursor.rowcount
                return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error en crear Departamento: {str(e)}'

  
##ACTUALIZAR AREA
def actualizarArea(area_id, area_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = """UPDATE area SET nombre_area = %s WHERE id_area = %s"""
                valores = (area_name, area_id)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_update = mycursor.rowcount
                return resultado_update 
        
    except Exception as e:
        return f'Se produjo un error al actualizar el área: {str(e)}'
 
#select tarjetas 
def lista_tarjetasBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_tarjeta, codigo_hexadecimal, estado_tarjeta FROM tarjetas_rfid"
                cursor.execute(querySQL,)
                tarjetasBD = cursor.fetchall()
        return tarjetasBD
    except Exception as e:
        print(f"Error en lista_tarjetas : {e}")
        return []
   
#añadir tarjeta
def agregarTarjeta(card_name):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = "INSERT INTO tarjetas_rfid (codigo_hexadecimal) VALUES (%s)"
                valores = (card_name,)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_insert = mycursor.rowcount
                return resultado_insert 
        
    except Exception as e:
        return f'Se produjo un error al añadir la tarjeta: {str(e)}'  

    
    
def eliminarTarjeta(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tarjetas_rfid WHERE id_tarjeta=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarTarjeta : {e}")
        return []
    
def cambiar_estado_tarjeta(id):
    try:
        # Conexión con la base de datos
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT estado_tarjeta FROM tarjetas_rfid WHERE id_tarjeta=%s"
                cursor.execute(querySQL, (id,))
                tarjeta = cursor.fetchone()              
                if tarjeta:
                    nuevo_estado = 'Inactiva' if tarjeta['estado_tarjeta'] == 'Activa' else 'Activa'
                    querySQL_update = "UPDATE tarjetas_rfid SET estado_tarjeta=%s WHERE id_tarjeta=%s"
                    cursor.execute(querySQL_update, (nuevo_estado, id))
                    conexion_MySQLdb.commit()
                    return True  # Indica que la operación fue exitosa
                else:
                    return False  # La tarjeta no se encontró
    except Exception as e:
        print(f"Error en cambiar_estado_tarjeta : {e}")
        return False  # En caso de error, retornamos False

    
#Historial sensores SELECT
def obtener_registros_sensores():
    try:
        # Conexión con la base de datos
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Consulta SQL
                querySQL = """
                SELECT 
                    d.nombre_departamento,
                    s.descripcion AS nombre_sensor,
                    h.valor,
                    h.descripcion
                FROM historial_sensores h
                JOIN sensores s ON h.id_sensor = s.id_sensor
                JOIN departamentos d ON s.id_departamento = d.id_departamento;
                """
                cursor.execute(querySQL)
                registros = cursor.fetchall()
                
                if registros:
                    return registros  
                else:
                    return None 
    except Exception as e:
        print(f"Error en obtener_registros_sensores: {e}")
        return None  
    
def obtener_edificios():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_edificio, nombre_edificio, direccion FROM edificios"
                cursor.execute(querySQL)
                edificios = cursor.fetchall()
        return edificios
    except Exception as e:
        print(f"Error en obtener_edificios: {e}")
        return []

def crear_edificio(nombre_edificio, direccion):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "INSERT INTO edificios (nombre_edificio, direccion) VALUES (%s, %s)"
                cursor.execute(querySQL, (nombre_edificio, direccion))
                conexion_MySQLdb.commit()
                resultado_insertar = cursor.rowcount
        return resultado_insertar
    except Exception as e:
        print(f"Error en crear_edificio: {e}")
        return []

def eliminar_edificio(id_edificio):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM edificios WHERE id_edificio=%s"
                cursor.execute(querySQL, (id_edificio,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminar_edificio: {e}")
        return []

