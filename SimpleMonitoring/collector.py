import asyncio
import ast
import configparser
import datetime
import os
import time
from client import ClientAgent
from database import DBclient


class Collector:

    def __init__(self, config_path='collector.ini', loop=None):
        self.loop=loop
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, config_path)
        self.config = configparser.ConfigParser()
        self.config.read(path)
        self.clients = {}
        self.dbClient = DBclient()
        if not loop:
            self.loop = asyncio.get_event_loop()

    def initialization_clients(self):
        for location in self.config:
            # print(location)
            if self.config.items(location):
                self.clients[location] = {}
                self.clients[location]['client'] = ClientAgent(self.config.get(location, 'host'), self.config.get(location, 'port'), loop=self.loop)
                self.clients[location]['monitoring'] = ast.literal_eval((self.config.get(location, 'monitoring')))#TODO change it and config

        # print(self.clients)
    async def fetch_data(self, future, client, data):
        print("IN fetch")
        func = getattr(client, data)
        future.set_result(await func())
        print(future._state)
        print("OUT fetch")

    def is_full_row(self, row):
        for column in row:
            if not column.done():
                print('return false')
                return False
        print('return True')
        return True

    async def push_row_db(self, table_name, row):
        while not self.is_full_row(row):#TODO Hmmm
            print('full: ', self.is_full_row(row))
            await asyncio.sleep(0)
            print('con')
        print('move')
        data = [column.result()['data'] for column in row]
        data.insert(0, datetime.datetime.now())
        await self.dbClient.fill_db(table_name, data)
        last = await self.dbClient.fetch_last_row(table_name)
        print(data)
        print(last)

    async def add_tasks(self):
        print(self.clients)
        for client_name, client_controler in self.clients.items():
            row_future = []#TODO think about row/future
            for num, monitoring_item in enumerate(client_controler['monitoring']):
                row_future.append(asyncio.Future(loop=self.loop))
                print(row_future)
                print("Create task: ", monitoring_item)
                self.loop.create_task(self.fetch_data(row_future[num], client_controler['client'], monitoring_item))
            # time.sleep(2)
            await self.push_row_db(client_name, row_future)

    async def task_scheduler(self, interval=1):
        while True:
            await self.add_tasks()
            await asyncio.sleep(interval)



# loop = asyncio.get_event_loop()
bone_colletor = Collector(loop=None)
bone_colletor.initialization_clients()
bone_colletor.loop.run_until_complete(bone_colletor.task_scheduler(interval=3))


# #test plot
# from bokeh.io import curdoc
# from bokeh.models import ColumnDataSource
# from bokeh.plotting import Figure
#
#
# def pull():
#     global loop, source, a
#     async def pulling_loop(interval=0):
#         global a
#         data = await bone_colletor.fetch_data(bone_colletor.clients['controler']['client'], 'cpu_percent')
#         print(data)
#         data_parsed = dict(x=[a], y=[data['data']])
#         print(data_parsed)
#         source.stream(data_parsed, 100)
#         time.sleep(interval)
#         a += 1
#     print(source)
#     loop.run_until_complete(pulling_loop())
# a = 0
# source = ColumnDataSource(dict(x=[], y=[]))
# fig = Figure()
# fig.line(source=source, x='x', y='y', line_width=2, alpha=.85, color='red')
#
#
# loop = asyncio.get_event_loop()
# curdoc().add_root(fig)
#
# curdoc().add_periodic_callback(pull, 100)
#
