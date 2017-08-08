import asyncio

import datetime

import time
from client import ClientAgent
from database import DBclient


class Collector:

    def __init__(self, db_config, agents_config, loop=None):
        self.loop = loop
        self.db_config = db_config
        self.agents_config = agents_config

        self.clients = {}

        self.dbClient = DBclient(self.db_config, self.agents_config)
        if not loop:
            self.loop = asyncio.get_event_loop()

    def initialization_clients(self):
        for agent, agent_config in self.agents_config.items():
            self.clients[agent] = {}
            self.clients[agent]['client'] = ClientAgent(agent_config['host'], agent_config['port'], loop=self.loop)
            self.clients[agent]['monitoring'] = agent_config['monitoring']
            print(self.clients)

    async def fetch_data(self, future, client, data):
        print("IN fetch")
        func = getattr(client, data)
        future.set_result(await func())
        print(future._state)
        print("OUT fetch")

    async def is_full_row(self, row, timeout=3):
        timeout = timeout + time.time()
        while time.time() < timeout:
            await asyncio.sleep(0.1)
            print('wait for task done')
            for column in row:

                print(row)
                if not column.done():
                    print('task NOT done')
                    break
                print('task  DONE')
                print(row)
                return True
        print('timeout for  done')
        return True

    async def push_row_db(self, table_name, row, timeout=3):
        await self.is_full_row(row, timeout=3)
        data = []
        for column in row:
            try:
                data.append(column.result()['data'])
            except asyncio.InvalidStateError:
                data.append(None)

        data.insert(0, datetime.datetime.now())
        await self.dbClient.fill_db(table_name, data)
        last = await self.dbClient.fetch_last_row(table_name)

    async def add_tasks(self, timeout=3):
        for client_name, client_controler in self.clients.items():
            row_future = []#TODO think about row/future
            print(client_name, client_controler)
            for num, monitoring_item in enumerate(client_controler['monitoring']):
                row_future.append(asyncio.Future(loop=self.loop))
                print("Create task: ", monitoring_item)
                self.loop.create_task(self.fetch_data(row_future[num], client_controler['client'], monitoring_item))
            self.loop.create_task(self.push_row_db(client_name, row_future, timeout))

    async def task_scheduler(self, interval=10, timeout=2):
        while True:
            await self.add_tasks(timeout)
            await asyncio.sleep(interval)

