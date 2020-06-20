FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pydbus \
    apt-transport-https \
    gnupg2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list

RUN apt-get update \
    && apt-get install -y kubectl \
    && rm -rf /var/lib/apt/lists/*

COPY service-mdns.sh /opt/ext-mdns/
COPY update_mdns.py /opt/ext-mdns/

ENTRYPOINT ["/opt/ext-mdns/service-mdns.sh"]
