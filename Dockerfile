# Usar la imagen base para Raspberry Pi con Debian
FROM balenalib/raspberry-pi-debian as build

# Actualizar el sistema y añadir las dependencias necesarias
RUN apt update -y && \
    apt upgrade -y && \
    apt install -y wget tar

# Descargar el archivo tar.gz desde el repositorio de GitHub
RUN wget -O /tmp/engine_3.1.80_armv7.tar.gz https://github.com/jordicb/docker-acestream-arm/raw/main/engine_3.1.80_armv7.tar.gz

# Extraer el archivo descargado en el directorio /tmp
RUN tar -xzf /tmp/engine_3.1.80_armv7.tar.gz -C /tmp

# Mover archivos y hacer configuraciones necesarias
RUN cd /tmp/acestream.engine && \
    mv androidfs/system / && \
    mv androidfs/acestream.engine / && \
    mkdir -p /storage && \
    mkdir -p /system/etc && \
    ln -s /etc/resolv.conf /system/etc/resolv.conf && \
    ln -s /etc/hosts /system/etc/hosts && \
    chown -R root:root /system && \
    find /system -type d -exec chmod 755 {} \; && \
    find /system -type f -exec chmod 644 {} \; && \
    chmod 755 /system/bin/* /acestream.engine/python/bin/python

# Si deseas construir la imagen con una configuración personalizada, descomenta la siguiente línea
# ADD acestream.conf  /acestream.engine/

# Exponer los puertos necesarios para AceStream
EXPOSE 8621 6878

# Definir el comando que se ejecutará cuando el contenedor se inicie
CMD ["/system/bin/acestream.sh"]
