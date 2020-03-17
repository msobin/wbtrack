from dependency_injector import containers, providers

from common.db import Db
from common.product_service import ProductService
from common.user_service import UserService


class Container(containers.DeclarativeContainer):
    db = providers.Factory(Db)
    user_service = providers.Factory(UserService, db=db)
    product_service = providers.Factory(ProductService, db=db)


container = Container

user_service: UserService = container.user_service()
product_service: ProductService = container.product_service()
