from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mqtt_host: str = "mqtt5"
    mqtt_port: int = 1883
    mqtt_username: Optional[str] = ""
    mqtt_password: Optional[str] = ""
    mqtt_keepalive: int = 60
    mqtt_reconnect_timeout: int = 3
    data_map: str = r"data/sensors_map.svg"

    model_config = SettingsConfigDict(env_file=".env")
