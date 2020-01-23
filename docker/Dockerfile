FROM python:3

RUN apt-get update \
    && apt-get install -y supervisor libpq-dev cron \
    && pip install --upgrade pip

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt
COPY ./docker/supervisord.conf /etc/supervisord.conf
COPY ./docker/crontab.yaml /etc/crontab.yaml

RUN pip install -r requirements.txt
RUN pip install yacron

CMD ["/usr/bin/supervisord", "-n", "-c",  "/etc/supervisord.conf"]