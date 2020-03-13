FROM python:3

RUN apt-get update \
    && apt-get install -y supervisor libpq-dev cron \
    && pip install --upgrade pip

WORKDIR /app

RUN pip install yacron

COPY ./app/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./docker/supervisord.conf /etc/supervisord.conf
COPY ./docker/crontab.yaml /etc/crontab.yaml

RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh > /usr/local/bin/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

CMD ["wait-for-it.sh", "-s" , "-t", "300", "rabbitmq:5672", "--", "/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.conf"]
