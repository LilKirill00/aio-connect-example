from aio_connect.filters import BaseFilter
from aio_connect.types import TypeLine


class SentByUserFilter(BaseFilter):
    async def __call__(self, line: TypeLine) -> bool:
        return line.user_id == line.author_id
