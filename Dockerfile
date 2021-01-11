FROM ubuntu:16.04
LABEL MAINTAINER="Bystroushaak"

RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip \
    supervisor \
    python \
    curl
RUN pip install -U wa-kat
RUN python -m textblob.download_corpora

RUN rm /etc/supervisor/supervisord.conf
ADD src/wa_kat/templates/conf/supervisord.conf /etc/supervisor/supervisord.conf
ADD src/wa_kat/templates/conf/wa-kat.service /lib/systemd/system/wa-kat.service

EXPOSE 8080

ENTRYPOINT service supervisor --full-restart && tail -f /var/log/supervisor/wa_kat-stdout*
