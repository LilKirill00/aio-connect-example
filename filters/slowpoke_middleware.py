import asyncio
from typing import Callable, Dict, Any, Awaitable

from aio_connect import BaseMiddleware
from aio_connect.types import ConnectObject


class SlowpokeMiddleware(BaseMiddleware):
    def __init__(self, sleep_sec: int):
        self.sleep_sec = sleep_sec

    async def __call__(
            self,
            handler: Callable[[ConnectObject, Dict[str, Any]], Awaitable[Any]],
            event: ConnectObject,
            data: Dict[str, Any],
    ) -> Any:
        await asyncio.sleep(self.sleep_sec)
        result = await handler(event, data)
        return result
