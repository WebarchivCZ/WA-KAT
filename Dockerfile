FROM ubuntu:14.04
MAINTAINER Bystroushaak

RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip \
    supervisor \
    curl
RUN pip install -U wa-kat
RUN python -m textblob.download_corpora

RUN rm /etc/supervisor/supervisord.conf
ADD src/wa_kat/templates/conf/supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 8080

ENTRYPOINT service supervisor restart && tail -f /var/log/supervisor/wa_kat-stdout*
