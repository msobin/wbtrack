import os

DB_USER = os.getenv('POSTGRES_WB_USER', 'wbuser')
DB_PASSWORD = os.getenv('POSTGRES_WB_PASSWORD', 'wbpassword')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', 5432)
DB = os.getenv('POSTGRES_WB_DB', 'wbtrack')

PRODUCT_REGEXP = r'https:\/\/[www.]*wildberries.\w{2}\/catalog\/\d+\/detail.aspx'

MAX_PRODUCT_COUNT = int(os.getenv('MAX_PRODUCT_COUNT', 30))

BOT_TOKEN = os.getenv('BOT_TOKEN')
NOTIFY_INTERVAL = 60 * 10

LOG_DIR = os.getenv('LOG_DIR', '/var/log/container')
DATA_DIR = os.getenv('DATA_DIR', '/etc/data')
