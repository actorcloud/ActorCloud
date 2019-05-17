FROM python:3.6.5-slim

COPY sources.list /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y supervisor \
    python-meld3 && \
    rm -rf /var/lib/apt/lists/* && \
    sed -i 's/^\(\[supervisord\]\)$/\1\nnodaemon=true/' /etc/supervisor/supervisord.conf

COPY codec.conf /etc/supervisor/conf.d/codec.conf

COPY . /opt/codec/

RUN mkdir -p /opt/tmp/logs && \
    pip install flask gunicorn -i https://pypi.douban.com/simple/ --default-timeout=30

EXPOSE 7002

WORKDIR /opt/codec

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
