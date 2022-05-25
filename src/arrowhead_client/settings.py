from pydantic import BaseSettings

class CloudSettings(BaseSettings):
    pass

class ClientSettings(BaseSettings):
    system_name: str
    address: str
    port: int
    keyfile: str
    certfile: str
    cafile: str
    config: CloudSettings = CloudSettings()

    class Config:
        env_prefix = 'python_arrowhead_'
