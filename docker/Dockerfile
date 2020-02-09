FROM python:3

RUN apt-get update \
    && apt-get install -y supervisor libpq-dev cron \
    && pip install --upgrade pip

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt

RUN pip install yacron
RUN pip install -r requirements.txt

COPY ./docker/supervisord.conf /etc/supervisord.conf
COPY ./docker/crontab.yaml /etc/crontab.yaml

CMD ["/usr/bin/supervisord", "-n", "-c",  "/etc/supervisord.conf"]