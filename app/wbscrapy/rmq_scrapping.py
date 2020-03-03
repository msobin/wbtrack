import json

import pika
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

import common.env as env
import common.rmq as rmq
from common.models import Product
from common.session import session
from wbscrapy.project.spiders.products_spider import ProductsSpider

connection = pika.BlockingConnection(rmq.get_url_parameters())
channel = connection.channel()

channel.exchange_declare(exchange=env.RMQ_EXCHANGE, exchange_type='direct')
queue = channel.queue_declare(env.RMQ_QUEUE_NEW_PRODUCT, durable=True)
channel.queue_bind(exchange=env.RMQ_EXCHANGE, queue=env.RMQ_QUEUE_NEW_PRODUCT, routing_key=env.RMQ_QUEUE_NEW_PRODUCT)

q_len = queue.method.message_count

product_ids = []


def message_callback(ch, method, properties, body):
    global q_len

    try:
        data = json.loads(body.decode('utf-8'))
        product_ids.append(data['product_id'])
    except json.JSONDecodeError:
        pass

    q_len -= 1
    if not q_len:
        ch.stop_consuming()


if q_len:
    channel.basic_consume(queue=env.RMQ_QUEUE_NEW_PRODUCT, on_message_callback=message_callback, auto_ack=True)
    channel.start_consuming()

connection.close()

products = session.query(Product).filter(Product.id.in_(set(product_ids))).all()

if products:
    settings = Settings()
    settings.setmodule('wbscrapy.project.settings', priority='project')
    process = CrawlerProcess(settings)
    process.crawl(ProductsSpider, products, session)
    process.start()

