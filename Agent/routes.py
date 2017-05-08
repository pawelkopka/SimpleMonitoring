from views import *


def setup_routes(app):
    app.router.add_get('/cpu_percent', Agnet.cpu_percent)
    app.router.add_get('/virtual_memory', Agnet.virtual_memory)
    app.router.add_get('/sensors_temperatures', Agnet.sensors_temperatures)
    app.router.add_get('/pid', Agnet.pid)