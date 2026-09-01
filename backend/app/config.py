from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend_port: int = 8000
    # Comma-separated list is supported (e.g. "http://localhost:5173,http://localhost:4173")
    # so local dev, `vite preview`, and a deployed frontend origin can all be allowed at once
    # without editing code -- just extend the .env value.
    frontend_origin: str = 'http://localhost:5173,http://localhost:4173,http://127.0.0.1:5173'
    artifacts_path: str = './ml/artifacts'
    log_level: str = 'INFO'

    class Config:
        env_file = '.env'
        extra = 'ignore'

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origin.split(',') if origin.strip()]


settings = Settings()
