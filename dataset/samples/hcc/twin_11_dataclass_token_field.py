import os
from dataclasses import dataclass, field


@dataclass
class WebhookSettings:
    endpoint: str = "https://hooks.example.com/deploy"
    api_token: str = field(default_factory=lambda: os.environ["WEBHOOK_TOKEN"])
    retries: int = 3


settings = WebhookSettings()
