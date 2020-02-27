import pika
import common.env as env


rmq_parameters = pika.URLParameters('amqp://{}:{}@rabbitmq/'.format(env.RABBITMQ_USER, env.RABBITMQ_PASS))
rmq_connection = pika.BlockingConnection(rmq_parameters)
rmq_channel = rmq_connection.channel()

rmq_channel.queue_declare(env.QUEUE_NEW_PRODUCTS, durable=True)
