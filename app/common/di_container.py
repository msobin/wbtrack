from dependency_injector import containers, providers

from common.db import Db
from common.user_service import UserService


class Container(containers.DeclarativeContainer):
    db = providers.Factory(Db)
    user_service = providers.Factory(UserService, db=db)


container = Container
user_service = container.user_service()
