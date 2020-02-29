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
channel.queue_declare(env.RMQ_QUEUE_WBSCRAPY, durable=True)

product_ids = []

while True:
    method_frame, header_frame, body = channel.basic_get(env.RMQ_QUEUE_WBSCRAPY)

    if method_frame:
        try:
            channel.basic_ack(method_frame.delivery_tag)

            data = json.loads(body.decode('utf-8'))
            product_ids.append(data['product_id'])
        except json.JSONDecodeError:
            pass
    else:
        break

products = session.query(Product).filter(Product.id.in_(set(product_ids))).all()

if products:
    settings = Settings()
    settings.setmodule('wbscrapy.project.settings', priority='project')
    process = CrawlerProcess(settings)
    process.crawl(ProductsSpider, products, session)
    process.start()

connection.close()
