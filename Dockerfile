FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    libnss-mdns \
    avahi-daemon \
    python3 \
    python3-pydbus \
    && rm -rf /var/lib/apt/lists/*

COPY service-mdns.sh /opt/ext-mdns/
COPY update_mdns.py /opt/ext-mdns/

ENTRYPOINT ["/opt/ext-mdns/service-mdns.sh"]
