from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from pulse_backend.db.models import User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


class UserService(SQLAlchemyAsyncRepositoryService[User]):
    repository_type = UserRepository
