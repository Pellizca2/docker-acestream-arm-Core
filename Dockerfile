# Usamos la imagen base de Alpine, que se pasa como argumento al construir
ARG ALPINE_IMAGE=python:3-alpine3.18

FROM ${ALPINE_IMAGE} as build

# Instalar herramientas necesarias: wget para descargar y tar para extraer
RUN apk add --no-cache wget tar

# Descargar el archivo tar.gz desde el repositorio de GitHub
RUN wget -O /tmp/engine_3.1.80_armv7.tar.gz https://github.com/jordicb/docker-acestream-arm/raw/main/engine_3.1.80_armv7.tar.gz

# Extraer el archivo descargado en el directorio /tmp
RUN tar -xzf /tmp/engine_3.1.80_armv7.tar.gz -C /tmp

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

# If you want build image with custom configuration, uncomment next line
# ADD acestream.conf  /acestream.engine/

EXPOSE 8621 6878


CMD "/system/bin/acestream.sh"
