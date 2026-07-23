from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Generous defaults - designed to never block normal human usage, only
# scripted/bot-level abuse. In-memory storage (no Redis) is fine for a
# single-instance deployment; if this ever runs across multiple backend
# replicas, this should move to a shared Redis backend so limits are
# counted across all instances instead of per-instance.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
)
