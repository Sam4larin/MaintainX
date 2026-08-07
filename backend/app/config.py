from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend_port: int = 8000
    frontend_origin: str = 'http://localhost:5173'
    artifacts_path: str = './ml/artifacts'
    log_level: str = 'INFO'

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings()
