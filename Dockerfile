FROM python:3.7-slim-buster

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y --no-install-recommends --fix-missing \
    python3-opencv \
    && pip install --no-cache-dir -r requirements.txt  \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/* \
    && rm -rf ~/.cache/pip/* \
    && apt-get purge -y --auto-remove \
    && apt-get clean all

WORKDIR /app

ADD . .

RUN ln -sf /dev/stdout logs/app.log \
    && ln -sf /dev/stdout logs/detector.log \
    && ln -sf /dev/stdout logs/utils.log

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["gunicorn", "-c", "python:config.gunicorn", "app"]
