import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
import random
import datetime

class DBclient(object):
    metadata = sa.MetaData()
    #TODO create Table from config
    controler1 = sa.Table('controler1', metadata,
                     sa.Column('time', sa.DateTime, primary_key=True),
                     sa.Column('cpu', sa.Float),
                     sa.Column('virtual_memory', sa.JSON))
    controler2 = sa.Table('controler2', metadata,
                     sa.Column('time', sa.DateTime, primary_key=True),
                     sa.Column('cpu', sa.Float),
                     sa.Column('virtual_memory', sa.JSON))

    map_tables = {'controler1': controler1, 'controler2': controler2}
    def __init__(self, loop=None):#TODO add parm to connetion
        #TODO create metadata from config
        self.loop = loop
        if not loop:
            self.loop = asyncio.get_event_loop()
        self.create_tables()
        self.loop.run_until_complete(self._init_engine())

    async def _init_engine(self):#TODO add param to conntion
        self.engine = await create_engine(host='127.0.0.1', user='postgres', password='ppp', database='test1')

    def create_tables(self):
        uri = 'postgresql://postgres:ppp@localhost:5432/test1'#TODO parse kwargs to uri
        engine = sa.create_engine(uri)
        self.metadata.create_all(engine)

    async def fill_db(self, table_name, data):
        print(table_name)
        print(data)
        async with self.engine.acquire() as conn:
            await conn.execute(self.map_tables[table_name].insert().values(data))

    async def fetch_db(self, table_name):
        async with self.engine.acquire() as conn:
            res = await conn.execute(self.map_tables[table_name].select())
            return await res.fetchall()

    async def fetch_last_row(self, table_name):
        async with self.engine.acquire() as conn:
            res = await conn.execute(self.map_tables[table_name].select().order_by(self.map_tables[table_name].c.time.desc()).limit(1))
            return await res.fetchall()

    async def go(self):
        await self.fill_db('controler1', (datetime.datetime.now(), 11, [23, 32, 45]))
        a = await self.fetch_db('controler1')
        print(type(a))
        print(a)
        b= await self.fetch_last_row('controler1')
        print(type(b))
        print(b)
        # await metadata.create_all(engine)
# loop = asyncio.get_event_loop()
# DBC = DBclient(loop=loop)
# DBC.create_tables()
# loop.run_until_complete(DBC.go())