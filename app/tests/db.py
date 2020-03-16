# import testing.postgresql
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
#
# class Db:
#     def __init__(self):
#         with testing.postgresql.Postgresql(port=54322) as postgresql:
#             self.engine = create_engine(postgresql.url())
#
#         self.session_maker = sessionmaker(bind=self.engine)
#
#     def get_session(self):
#         return self.session_maker()
