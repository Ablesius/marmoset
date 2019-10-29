from . import config, webserver

CONFIG = config.load_config()

APP = webserver.app(config)
