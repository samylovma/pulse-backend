from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from pulse_backend.db.models import Post


class PostRepository(SQLAlchemyAsyncRepository[Post]):
    model_type = Post


class PostService(SQLAlchemyAsyncRepositoryService[Post]):
    repository_type = PostRepository
