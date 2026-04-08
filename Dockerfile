FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    suricata \
    suricata-update \
    iproute2 \
    tcpdump \
    curl \
    wget \
    nano \
    python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/suricata/rules /var/log/suricata /var/run/suricata

COPY rules/local.rules /etc/suricata/rules/local.rules
COPY config/suricata.yaml /etc/suricata/suricata.yaml

CMD ["suricata", "-c", "/etc/suricata/suricata.yaml", "-i", "eth0"]