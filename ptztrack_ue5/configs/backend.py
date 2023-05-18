"""
Variables, which use for backend
"""
from os import environ, path

from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class BackendError(Exception):
    """
    Класс ошибок возникающих на стороне бэкенда
    """
    pass

# JSON path folder is the project folder
PROJECT_PATH = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
JSON_PATH = path.join(PROJECT_PATH, "jsons")


# FastAPI settings
IP_ADDR_FASTAPI = environ.get("IP_ADDR_FASTAPI")
PORT_FASTAPI = environ.get("PORT_FASTAPI")
if ( IP_ADDR_FASTAPI is None or \
        PORT_FASTAPI is None ):
    raise BackendError(
        "IP_ADDR_FASTAPI or PORT_FASTAPI are not set"
    )
PORT_FASTAPI = int(PORT_FASTAPI)

# URL constraction constants
VERSION_PROTOCOL = "http://"
PATH_SERVER_FOR_REQUEST = "remote/object/call"
PATH_SERVER_FOR_INFO = "remote/info"
IP_ADDR_UNREAL_REMOTE_CONTROL = environ.get("IP_ADDR_UNREAL_REMOTE_CONTROL")
PORT_UNREAL_REMOTE_CONTROL = environ.get("PORT_UNREAL_REMOTE_CONTROL")
if ( IP_ADDR_UNREAL_REMOTE_CONTROL is None or \
        PORT_UNREAL_REMOTE_CONTROL is None ):
    raise BackendError(
        "IP_ADDR_UNREAL_REMOTE_CONTROL or PORT_UNREAL_REMOTE_CONTROL are not set"
    )
URL_UNREAL_SERVER_STRING = (
    f"{VERSION_PROTOCOL}{IP_ADDR_UNREAL_REMOTE_CONTROL}:{PORT_UNREAL_REMOTE_CONTROL}"
)

# onvif settings
WSDL_PATH = environ.get("WSDL_PATH")
if WSDL_PATH is None:
    raise BackendError("WSDL_PATH is not set")

# lambda function for unreal computing positions and zoom
pantilt_x_coef = lambda x: x * 170
pantilt_y_coef = lambda y: y * 90
zoom_coef = lambda zoom: zoom * 50 + 10
