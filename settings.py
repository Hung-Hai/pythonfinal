import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get configuration value from environment variables.
    If the key does not exist, return the default value.
    """
    return os.getenv(key, default)


### DEFAULT SETTINGS

POSTGRES_PASSWORD = get_config(key="POSTGRES_PASSWORD", default="password")
POSTGRES_USER = get_config(key="POSTGRES_USER", default="user")
POSTGRES_DB = get_config(key="POSTGRES_DB", default="database")
SECRET_KEY = get_config(key="SECRET_KEY", default="secr")
ALGORITHM = get_config(key="ALGORITHM", default="al")
ACCESS_TOKEN_EXPIRE_MINUTES = get_config(key="ACCESS_TOKEN_EXPIRE_MINUTES", default="accessexpire")
###
