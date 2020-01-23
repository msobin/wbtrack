from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import common.env as env

engine = create_engine('postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(
    user=env.DB_USER,
    password=env.DB_PASSWORD,
    host=env.DB_HOST,
    port=env.DB_PORT,
    database=env.DB,
    echo=False
))

session = sessionmaker(bind=engine)()
