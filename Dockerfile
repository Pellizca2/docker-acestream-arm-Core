FROM balenalib/raspberry-pi-debian as build

RUN apt update -y && apt upgrade -y && \
    apt install -y wget tar

RUN wget -O /tmp/engine_3.1.80_armv7.tar.gz https://github.com/jordicb/docker-acestream-arm/raw/main/engine_3.1.80_armv7.tar.gz

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

# Asegurarse de que el script sea ejecutable
RUN chmod +x /system/bin/acestream.sh

# Exponer los puertos necesarios
EXPOSE 8621 6878

# Ejecutar el script usando /bin/sh
CMD ["/bin/sh", "/system/bin/acestream.sh"]
