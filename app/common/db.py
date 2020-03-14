from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import common.env as env


class Db:
    def __init__(self):
        self.engine = create_engine('postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(
            user=env.DB_USER,
            password=env.DB_PASS,
            host=env.DB_HOST,
            port=env.DB_PORT,
            database=env.DB,
            echo=True
        ))

        self.session_maker = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.session_maker()
