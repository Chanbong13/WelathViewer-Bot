from __future__ import annotations

from config import Settings
from src.line_webhook import create_app


settings = Settings()
app = create_app(settings)


if __name__ == "__main__":
    app.run(host=settings.app_host, port=settings.app_port)
