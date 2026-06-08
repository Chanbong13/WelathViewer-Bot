from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class IncomingMessage:
    user_id: str
    timestamp: str
    platform: str
    message: str
    conversation_context: dict | None = None


class MessageReceiver:
    def create_input(self, user_id: str, message: str, platform: str = "LINE", conversation_context: dict | None = None) -> IncomingMessage:
        return IncomingMessage(
            user_id=user_id,
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
            platform=platform,
            message=message,
            conversation_context=conversation_context or {},
        )
