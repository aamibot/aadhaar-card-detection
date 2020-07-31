FROM python:3.7-slim-buster

COPY requirements.txt .

ENV BUILD_DEPS="build-essential" \
    APP_DEPS=""

RUN apt-get update \
    && apt-get install -y ${BUILD_DEPS} ${APP_DEPS} --no-install-recommends --fix-missing \
    python3-opencv \
    && pip install --no-cache-dir -r requirements.txt  \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/* \
    && rm -rf ~/.cache/pip/* \
    && rm -rf /usr/share/doc \
    && rm -rf /usr/share/man \
    && apt-get purge -y --auto-remove ${BUILD_DEPS} \
    && apt-get clean 

WORKDIR /app

ADD . .

RUN ln -sf /dev/stdout logs/app.log \
    && ln -sf /dev/stdout logs/detector.log \
    && ln -sf /dev/stdout logs/utils.log

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "app"]
