from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from pulse_backend.db.models import Friend


class FriendRepository(SQLAlchemyAsyncRepository[Friend]):
    model_type = Friend


class FriendService(SQLAlchemyAsyncRepositoryService[Friend]):
    repository_type = FriendRepository
