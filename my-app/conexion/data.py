from flask import Flask, request, jsonify
import serial
import threading
from datetime import datetime
from conexionBD import connectionBD

# Configuración de los puertos seriales
puerto1 = serial.Serial(port='COM6', baudrate=9600, timeout=1)  # Arduino Mega
puerto2 = serial.Serial(port='COM7', baudrate=9600, timeout=1)  # Arduino Uno (CAMBIA SEGÚN NECESARIO)

app = Flask(__name__)

# Función para validar tarjetas RFID y registrar acceso
def registrar_y_validar_tarjeta(UID):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                query_verificar = """
                SELECT COUNT(*) FROM usuarios 
                JOIN tarjetas_rfid ON usuarios.id_tarjeta = tarjetas_rfid.id_tarjeta 
                WHERE tarjetas_rfid.codigo_hexadecimal = %s
                """
                cursor.execute(query_verificar, (UID,))
                existe = cursor.fetchone()[0] > 0

                if existe:
                    estado = "Permitido"
                    puerto1.write(b"ABRIR\n")  # 🔴 Responder al Arduino para que abra la puerta
                else:
                    estado = "Denegado"

                fecha_hora = datetime.now()
                query_insertar = """
                INSERT INTO accesos (id_tarjeta, fecha, estado) 
                VALUES ((SELECT id_tarjeta FROM tarjetas_rfid WHERE codigo_hexadecimal = %s), %s, %s)
                """
                cursor.execute(query_insertar, (UID, fecha_hora, estado))
                conexion_MySQLdb.commit()
    
    except Exception as e:
        print(f"Error en registrar_y_validar_tarjeta: {e}")

# Función para guardar datos de temperatura
def guardar_sensor_temperatura(temperatura):
    try:
        temperatura = float(temperatura.strip())
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                fecha_alerta = datetime.now()
                querySQL = """
                    INSERT INTO historial_sensores (id_sensor, fecha, valor, descripcion)
                    VALUES (
                        (SELECT id_sensor FROM sensores WHERE tipo_sensor = 'temperatura' LIMIT 1), 
                        %s, %s, 'Registro de temperatura'
                    )
                """
                cursor.execute(querySQL, (fecha_alerta, temperatura))
                conexion_MySQLdb.commit()
                print(f"Temperatura {temperatura} guardada correctamente en la BD.")
    except ValueError:
        print(f"Error: La temperatura '{temperatura}' no es válida.")
    except Exception as e:
        print(f"Error en guardar_sensor_temperatura: {e}")

# Función para guardar datos de detección de humo
def guardar_sensor_humo(valor):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                fecha_alerta = datetime.now()
                querySQL = """
                    INSERT INTO historial_sensores (id_sensor, fecha, valor, descripcion)
                    VALUES (
                        (SELECT id_sensor FROM sensores WHERE tipo_sensor = 'gas' LIMIT 1), 
                        %s, %s, 'Registro de humo'
                    )
                """
                cursor.execute(querySQL, (fecha_alerta, valor))
                conexion_MySQLdb.commit()
    except Exception as e:
        print(f"Error en guardar_sensor_humo: {e}")

# Función para guardar datos del sensor de contacto
def guardar_sensor_contacto(estado):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                fecha_alerta = datetime.now()
                descripcion = "Ventana Segura" if estado == "SEGURA" else "Ventana Abierta/Insegura"
                querySQL = """
                    INSERT INTO historial_sensores (id_sensor, fecha, valor, descripcion)
                    VALUES (
                        (SELECT id_sensor FROM sensores WHERE tipo_sensor = 'contacto' LIMIT 1), 
                        %s, %s, %s
                    )
                """
                cursor.execute(querySQL, (fecha_alerta, estado, descripcion))
                conexion_MySQLdb.commit()
    except Exception as e:
        print(f"Error en guardar_sensor_contacto: {e}")

# Función para guardar datos del sensor de agua (lluvia)
def guardar_sensor_lluvia(estado):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                fecha_alerta = datetime.now()
                descripcion = "Está lloviendo" if estado == "LLUEVE" else "No hay lluvia"
                querySQL = """
                    INSERT INTO historial_sensores (id_sensor, fecha, valor, descripcion)
                    VALUES (
                        (SELECT id_sensor FROM sensores WHERE tipo_sensor = 'lluvia' LIMIT 1), 
                        %s, %s, %s
                    )
                """
                cursor.execute(querySQL, (fecha_alerta, estado, descripcion))
                conexion_MySQLdb.commit()
    except Exception as e:
        print(f"Error en guardar_sensor_lluvia: {e}")

# Función para guardar eventos del servo
def guardar_evento_servo():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                fecha_alerta = datetime.now()
                querySQL = """
                    INSERT INTO historial_sensores (id_sensor, fecha, valor, descripcion)
                    VALUES (
                        (SELECT id_sensor FROM sensores WHERE tipo_sensor = 'servo' LIMIT 1), 
                        %s, %s, 'Servo activado'
                    )
                """
                cursor.execute(querySQL, (fecha_alerta, "ACTIVADO"))
                conexion_MySQLdb.commit()
    except Exception as e:
        print(f"Error en guardar_evento_servo: {e}")

# Función para leer datos del puerto serial
def leer_datos_puerto(puerto, nombre_puerto):
    try:
        while True:
            if puerto.in_waiting > 0:
                linea = puerto.readline().decode('utf-8').strip()
                if ':' in linea:
                    cabecera, contenido = linea.split(":", 1)
                    print(f"Datos recibidos ({nombre_puerto}): {linea}")

                    if cabecera == "UID":
                        registrar_y_validar_tarjeta(contenido)
                    elif cabecera == "TEMPERATURA":
                        guardar_sensor_temperatura(contenido)
                    elif cabecera == "HUMO":
                        guardar_sensor_humo(contenido)
                    elif cabecera == "VENTANA":
                        guardar_sensor_contacto(contenido)
                    elif cabecera == "AGUA":
                        guardar_sensor_lluvia(contenido)
                    elif cabecera == "SERVO":
                        guardar_evento_servo()
                else:
                    print(f"Línea no válida ({nombre_puerto}): {linea}")
    except Exception as e:
        print(f"Error en leer_datos_puerto ({nombre_puerto}): {e}")

if __name__ == "__main__":
    # Crear hilos para leer de ambos puertos
    hilo_puerto1 = threading.Thread(target=leer_datos_puerto, args=(puerto1, "Arduino Mega (COM6)"))
    hilo_puerto2 = threading.Thread(target=leer_datos_puerto, args=(puerto2, "Arduino Uno (COM7)"))

    # Iniciar los hilos
    hilo_puerto1.start()
    hilo_puerto2.start()

    # Mantener el programa principal en ejecución
    hilo_puerto1.join()
    hilo_puerto2.join()
