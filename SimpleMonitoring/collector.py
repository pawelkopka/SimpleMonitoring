import asyncio
import ast
import configparser
import os
import time
from client import ClientAgent

class Collector:

    def __init__(self, config_path='collector.ini', loop=None):
        self.loop=loop
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, config_path)
        self.config = configparser.ConfigParser()
        self.config.read(path)
        self.clients = {}

    def initialization_clients(self):
        for location in self.config:
            # print(location)
            if self.config.items(location):
                self.clients[location] = {}
                self.clients[location]['client'] = ClientAgent(self.config.get(location, 'host'), self.config.get(location, 'port'), loop=self.loop)
                self.clients[location]['monitoring'] = ast.literal_eval((self.config.get(location, 'monitoring')))#TODO change it and config
        # print(self.clients)
    async def fetch_data(self, client, data):
        func = getattr(client, data)
        return await func()

    async def pull_data(self):
        print(self.clients)
        for client_name, client_controler in self.clients.items():
            for monitoring_item in client_controler['monitoring']:
                # print(monitoring_item)
                data = self.fetch_data(client_controler['client'], monitoring_item)#TODO fix it
                print(data)




bone_colletor = Collector()
bone_colletor.initialization_clients()
# # a.pulling_loop()

# # a.pull_data()

#test plot
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure


def pull():
    global loop, source, a
    async def pulling_loop(interval=0):
        global a
        data = await bone_colletor.fetch_data(bone_colletor.clients['controler']['client'], 'cpu_percent')
        print(data)
        data_parsed = dict(x=[a], y=[data['data']])
        print(data_parsed)
        source.stream(data_parsed, 100)
        time.sleep(interval)
        a += 1
    print(source)
    loop.run_until_complete(pulling_loop())
a = 0
source = ColumnDataSource(dict(x=[], y=[]))
fig = Figure()
fig.line(source=source, x='x', y='y', line_width=2, alpha=.85, color='red')

# pulling_loop()
loop = asyncio.get_event_loop()
curdoc().add_root(fig)
curdoc().add_periodic_callback(pull, 100)
#
# loop=asyncio.get_event_loop()
# loop.run_until_complete(pulling_loop())
# loop.close()
