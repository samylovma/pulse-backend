from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from pulse_backend.db.models import Session


class SessionRepository(SQLAlchemyAsyncRepository[Session]):
    model_type = Session


class SessionService(SQLAlchemyAsyncRepositoryService[Session]):
    repository_type = SessionRepository
