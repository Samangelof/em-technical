from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
import os


load_dotenv()

def get_env_variable(env_variable: str, cast: type = str):
    value = os.getenv(env_variable)
    if value is None:
        raise ImproperlyConfigured(f'Set {env_variable} environment variable')
    try:
        if cast is bool:
            return value.lower() in ("true", "1", "yes")
        return cast(value)
    except Exception:
        raise ImproperlyConfigured(f'Could not cast {env_variable} to {cast}')
