from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from common.models import Product
from common.session import session
from wbscrapy.project.spiders.products_spider import ProductsSpider

settings = Settings()
settings.setmodule('wbscrapy.project.settings', priority='project')
process = CrawlerProcess(settings)

offset = 0
batch_size = process.settings.get('CONCURRENT_REQUESTS', 16) * 100

while True:
    products = session.query(Product).limit(batch_size).offset(offset).all()

    if not products:
        break

    process.crawl(ProductsSpider, products, session)
    offset += batch_size

process.start()
