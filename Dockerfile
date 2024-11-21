FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt /app/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . /app/

# Expón el puerto
EXPOSE 5000

# Ejecutar la aplicación
CMD ["python", "app/main.py"]
