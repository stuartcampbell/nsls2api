from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pass_api_key: str
    pass_api_url: str = "https://passservices.bnl.gov/passapi"
    active_directory_server: str
    active_directory_server_list: str
    n2sn_user_search: str
    n2sn_group_search: str
    bnlroot_ca_certs_file: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
    return Settings()
