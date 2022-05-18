from enum import Enum

class AppMode(Enum):
    WEB = "WEB"
    LOCAL = "LOCAL"
    DEV = "DEV"

_resources = {
    AppMode.WEB: '/home/pla-multi-checker-web/static/',
    AppMode.LOCAL: './static/',
    AppMode.DEV: './static/'
}

APP_MODE = AppMode.WEB
RESOURCE_PATH = _resources[APP_MODE]