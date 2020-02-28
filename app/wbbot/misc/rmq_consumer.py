import threading

import pika

import common.env as env


class RMQConsumer(threading.Thread):
    def __init__(self, queue, message_callback, *args, **kwargs):
        super(RMQConsumer, self).__init__(*args, **kwargs)

        self.queue = queue
        self.message_callback = message_callback

    def run(self):
        connection = pika.BlockingConnection(
            pika.URLParameters('amqp://{}:{}@rabbitmq/'.format(env.RABBITMQ_USER, env.RABBITMQ_PASS)))

        channel = connection.channel()
        channel.queue_declare(self.queue, durable=True)

        channel.basic_consume(self.queue, on_message_callback=self.message_callback)
        channel.start_consuming()

    # def on_message_callback(channel, method, properties, body):
    #
    #     channel.basic_ack(method.delivery_tag)
