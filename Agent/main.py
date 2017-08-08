import configparser
import os
from aiohttp import web
from routes import setup_routes


def create_app(loop=None, config_path='agent.ini') -> web.Application:
    """
    :param path_config_file: path to config file
    :return: web application created by aiohttp
    """
    # config
    path = os.path.dirname(os.path.realpath(__file__))
    print(path)
    path = os.path.join(path, config_path)
    print(path)
    config = configparser.ConfigParser()
    config.read(path)
    # app
    app = web.Application(loop=loop)
    app.update(host=config.get('DEFAULT', 'host'),
               debug=bool(config.get('DEFAULT', 'debug')),
               port=int(config.get('DEFAULT', 'port')))

    setup_routes(app)
    return app
