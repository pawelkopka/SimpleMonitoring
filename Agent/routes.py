from views import *


def setup_routes(app):
    app.router.add_get('/cpu_percent', cpu_percent)
    app.router.add_get('/virtual_memory', virtual_memory)
    app.router.add_get('/sensors_temperatures', sensors_temperatures)
    app.router.add_get('/pid', pid)