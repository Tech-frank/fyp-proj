from dataclasses import dataclass


@dataclass
class WebhookSettings:
    endpoint: str = "https://hooks.example.com/deploy"
    api_token: str = "whk_7Gd9sP2qL4xZ8cV1bN6m"
    retries: int = 3


settings = WebhookSettings()
