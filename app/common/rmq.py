import pika

import common.env as env


def get_url_parameters():
    return pika.URLParameters('amqp://{}:{}@rabbitmq/'.format(env.RMQ_USER, env.RMQ_PASS))
