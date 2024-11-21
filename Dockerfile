# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos y el proyecto a la imagen
COPY requirements.txt requirements.txt
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto 5000 donde Flask se ejecuta
EXPOSE 5000

# Establece el comando para ejecutar la app en el contenedor
CMD ["flask", "run", "--host=0.0.0.0"]
