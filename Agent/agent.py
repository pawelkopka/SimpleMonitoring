from main import create_app
from aiohttp import web

if __name__ == '__main__':

    web.run_app(create_app())
