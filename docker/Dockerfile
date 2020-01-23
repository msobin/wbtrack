FROM python:3

RUN apt-get update \
    && apt-get install -y supervisor libpq-dev cron \
    && pip install --upgrade pip

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install yacron
COPY ./docker/crontab.yaml /etc/crontab.yaml

COPY ./docker/supervisord.conf /etc/supervisord.conf
CMD ["/usr/bin/supervisord", "-n", "-c",  "/etc/supervisord.conf"]