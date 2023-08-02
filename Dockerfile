FROM ubuntu:22.04
ARG TARGETPLATFORM
ARG BUILDPLATFORM

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pydbus \
    apt-transport-https \
    gnupg2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then \ 
        curl -LO "https://dl.k8s.io/release/v1.27.4/bin/linux/amd64/kubectl" && \
        install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl; \
    elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        curl -LO "https://dl.k8s.io/release/v1.27.4/bin/linux/arm64/kubectl" && \
        install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl; \
    fi

COPY service-mdns.sh /opt/ext-mdns/
COPY update_mdns.py /opt/ext-mdns/

ENTRYPOINT ["/opt/ext-mdns/service-mdns.sh"]
