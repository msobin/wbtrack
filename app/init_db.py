from common.session import session
import common.env as env

session.connection().connection.set_isolation_level(0)
session.execute(f'CREATE DATABASE {env.DB}')
session.execute(f"CREATE USER {env.DB_USER} WITH PASSWORD '{env.DB_PASSWORD}'")
session.execute(f'GRANT ALL PRIVILEGES ON DATABASE {env.DB} to {env.DB_USER}')
session.connection().connection.set_isolation_level(1)

