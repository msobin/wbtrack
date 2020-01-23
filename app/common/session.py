from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

engine = create_engine('postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(
    user=os.getenv('POSTGRES_WB_USER', 'wbuser'),
    password=os.getenv('POSTGRES_WB_PASSWORD', 'wbpassword'),
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', 5432),
    database=os.getenv('POSTGRES_WB_DB', 'wbtrack'),
    echo=True
))

session = sessionmaker(bind=engine)()


