import serial
from datetime import datetime
from flask import Flask, jsonify
import mysql.connector

def connectionBD():
    print("ENTRO A LA CONEXION")
    try:
        connection = mysql.connector.connect(
            host="35.224.172.30",
            port=3306,
            user="root",
            passwd="GrupoProyecto1!",
            database="Domus",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            raise_on_warnings=True
        )
        if connection.is_connected():
            print("Conexión exitosa a la BD")
            return connection
    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")

# Configuración del puerto serial
arduino = serial.Serial(port='COM13', baudrate=9600, timeout=1)

app = Flask(__name__)

def guardar_sensor_humo(valor):
    try:
        valor = float(valor.strip())
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                querySQL = "INSERT INTO sensores (tipo_sensor, estado, descripcion, id_departamento) VALUES (%s, %s, %s, %s)"
                estado = 1 if valor > 5 else 0  # 1 = alerta, 0 = normal
                descripcion = f"Nivel de humo detectado: {valor}"
                id_departamento = 1  # Se puede cambiar según la lógica deseada
                cursor.execute(querySQL, ('gas', estado, descripcion, id_departamento))
                conexion_MySQLdb.commit()
    except ValueError:
        print(f"Error: El valor '{valor}' no es válido.")
    except Exception as e:
        print(f"Error en guardar_sensor_humo: {e}")

def registrar_y_validar_tarjeta(UID):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                # Verificar si la tarjeta está registrada en la base de datos por id_tarjeta
                query_verificar = "SELECT id_tarjeta FROM tarjetas_rfid WHERE codigo_hexadecimal = %s"
                cursor.execute(query_verificar, (UID,))
                tarjeta = cursor.fetchone()
                cursor.nextset()  # Limpiar posibles resultados no leídos

                if tarjeta:
                    # Si la tarjeta existe, obtener su id_tarjeta
                    id_tarjeta = tarjeta[0]
                    
                    # Verificar si el id_tarjeta está asociado a algún usuario
                    query_usuario = "SELECT COUNT(*) FROM usuarios WHERE id_tarjeta = %s"
                    cursor.execute(query_usuario, (id_tarjeta,))
                    existe_usuario = cursor.fetchone()[0] > 0
                    cursor.nextset()  # Limpiar posibles resultados no leídos

                    # Definir el estado en función de si el usuario existe
                    estado = "Activo" if existe_usuario else "Inactivo"
                else:
                    # Si la tarjeta no existe, establecer el estado como Inactivo
                    estado = "Inactivo"
                
                # Insertar la información de la tarjeta y su estado en la tabla
                query_insertar = "INSERT INTO tarjetas_rfid (codigo_hexadecimal, estado_tarjeta) VALUES (%s, %s)"
                cursor.execute(query_insertar, (UID, estado))
                conexion_MySQLdb.commit()

                # Accionar el Arduino dependiendo del estado de la tarjeta
                if estado == "Activo":
                    arduino.write(b"ABRIR")
                    return jsonify({'status': 'access_granted'}), 200
                else:
                    return jsonify({'status': 'access_denied'}), 403

    except Exception as e:
        print(f"Error en registrar_y_validar_tarjeta: {e}")
        return jsonify({'status': 'error'}), 500


def leer_datos_serial():
    print("Sistema iniciado.")
    try:
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                print(f"Datos recibidos: {linea}")  # Agrega una depuración aquí
                if ":" in linea:
                    cabecera, contenido = linea.split(":", 1)

                    if cabecera == "UID":
                        with app.app_context():
                            registrar_y_validar_tarjeta(contenido)
                    elif cabecera == "HUMO":
                        guardar_sensor_humo(contenido)        
                else:
                    print(f"Formato incorrecto: {linea}")
    except Exception as e:
        print(f"Error en leer_datos_serial: {e}")


if __name__ == "__main__":
    leer_datos_serial()