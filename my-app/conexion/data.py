from flask import Flask, request, jsonify
import serial
import threading
from datetime import datetime
from conexionBD import connectionBD


# Configuración de los puertos seriales
puerto1 = serial.Serial(port='COM6', baudrate=9600, timeout=1)

app = Flask(__name__)

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

                estado = "Permitido" if existe else "Denegado"
                fecha_hora = datetime.now()
                query_insertar = "INSERT INTO accesos (id_tarjeta, fecha) VALUES ((SELECT id_tarjeta FROM tarjetas_rfid WHERE codigo_hexadecimal = %s), %s)"
                cursor.execute(query_insertar, (UID, fecha_hora, estado))
                conexion_MySQLdb.commit()

                if estado == "Permitido":
                    puerto1.write(b"ABRIR")
    
    except Exception as e:
        print(f"Error en registrar_y_validar_tarjeta: {e}")
from datetime import datetime

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
                cursor.execute(querySQL, (fecha_alerta, temperatura, id_usuario_encargado,))
                conexion_MySQLdb.commit()
                print(f"Temperatura {temperatura} guardada correctamente en la BD.")
    except ValueError:
        print(f"Error: La temperatura '{temperatura}' no es válida.")
    except Exception as e:
        print(f"Error en guardar_sensor_temperatura: {e}")


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
                cursor.execute(querySQL, (fecha_alerta, valor, id_usuario_encargado,))
                conexion_MySQLdb.commit()
    except Exception as e:
        print(f"Error en guardar_sensor_humo: {e}")

def leer_datos_puerto(puerto, nombre_puerto):
    """Leer datos de un puerto serial."""
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
                else:
                    print(f"Línea no válida ({nombre_puerto}): {linea}")
    except Exception as e:
        print(f"Error en leer_datos_puerto ({nombre_puerto}): {e}")

if __name__ == "__main__":
    # Crear hilos para leer de cada puerto
    hilo_puerto1 = threading.Thread(target=leer_datos_puerto, args=(puerto1, "COM3"))

    # Iniciar los hilos
    hilo_puerto1.start()

    # Mantener el programa principal en ejecución
    hilo_puerto1.join()