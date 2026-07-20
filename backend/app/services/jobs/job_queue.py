from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger("creatoros.jobs")


class JobQueue:
    """
    Minimal in-process background job runner.

    Public interface (`enqueue`) matches the shape a future
    Celery/Redis-backed queue would expose, so swapping the
    implementation later won't require touching calling code.
    """

    def __init__(self, max_concurrent: int = 2):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._tasks: set[asyncio.Task] = set()

    def enqueue(self, coro_factory: Callable[[], Awaitable[None]]) -> None:
        task = asyncio.create_task(self._run(coro_factory))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _run(self, coro_factory: Callable[[], Awaitable[None]]) -> None:
        async with self._semaphore:
            try:
                await coro_factory()
            except Exception:
                logger.exception("Background job failed")


job_queue = JobQueue(max_concurrent=2)
