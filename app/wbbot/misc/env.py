import os

PRODUCT_REGEXP = r'https:\/\/[www.]*wildberries.\w{2}\/catalog\/\d+\/detail.aspx'
MAX_PRODUCT_COUNT = os.getenv('MAX_PRODUCT_COUNT', 100)
BOT_TOKEN = os.getenv('BOT_TOKEN')
NOTIFY_INTERVAL = 60 * 10
