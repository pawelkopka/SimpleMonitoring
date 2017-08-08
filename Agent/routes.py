from views import *


def setup_routes(app):
    agent = Agent()
    app.router.add_get('/cpu_percent', agent.cpu_percent)
    app.router.add_get('/virtual_memory', agent.virtual_memory)
    app.router.add_get('/sensors_temperatures', agent.sensors_temperatures)
    app.router.add_get('/pid', agent.pid)
