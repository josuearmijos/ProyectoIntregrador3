FROM python:3.11-slim-buster

WORKDIR /python-docker

# Copiar el archivo requirements.txt y instalar dependencias
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copiar todo el código al contenedor
COPY . .

# Exponer el puerto
EXPOSE 8080

# Ejecutar la aplicación Flask
CMD ["python", "-m", "flask", "--app", "my-app/run", "run", "--host=0.0.0.0", "--port=8080"]
