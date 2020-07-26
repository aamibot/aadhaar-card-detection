FROM python:3.7-slim-buster

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
    python3-opencv \
    && apt-get clean && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt && \
    rm -rf ~/.cache/pip/* 

WORKDIR /app

COPY . .

ENTRYPOINT ["gunicorn","--bind=0.0.0.0:4000","--workers=4"]

CMD ["app"]
