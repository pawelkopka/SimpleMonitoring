import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa


class DBclient(object):

    def __init__(self, db_config, agents_config, loop=None):
        self.loop = loop
        if not loop:
            self.loop = asyncio.get_event_loop()
        self.db_config = db_config
        self.BuilderDB = BuildDB(db_config)
        self.BuilderDB.setup_metadata(agents_config)
        self.BuilderDB.build_db()
        self.loop.run_until_complete(self._init_engine())

    async def _init_engine(self):
        self.engine = await create_engine(host=self.db_config['host'],
                                          user=self.db_config['user'],
                                          password=self.db_config['password'],
                                          database=self.db_config['database']
                                          )

    async def fill_db(self, table_name, data):
        async with self.engine.acquire() as conn:
            await conn.execute(self.BuilderDB.metadata_controller[table_name].insert().values(data))

    async def fetch_db(self, table_name):
        async with self.engine.acquire() as conn:
            res = await conn.execute(self.BuilderDB.metadata_controller[table_name].select())
            return await res.fetchall()

    async def fetch_last_row(self, table_name):
        async with self.engine.acquire() as conn:
            res = await conn.execute(self.BuilderDB.metadata_controller[table_name].select().order_by(self.BuilderDB.metadata_controller[table_name].c.time.desc()).limit(1))
            return await res.fetchall()


class BuildDB(object):
    MAP_DB_TYPE = {'float': sa.FLOAT, 'json': sa.JSON}

    def __init__(self, db_config):
        self.metadata = sa.MetaData()
        self.db_config = db_config
        self.metadata_controller = {}

    @property
    def uri(self):
        uri = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            user=self.db_config['user'],
            password=self.db_config['password'],
            host=self.db_config['host'],
            port=self.db_config['port'],
            database=self.db_config['database']
        )
        return uri

    def build_db(self):

        engine = sa.create_engine(self.uri)
        self.metadata.create_all(engine)

    def setup_metadata(self, agents_config):
        for agent_name, agent_config in agents_config.items():
            columns = [sa.Column('time', sa.DateTime, primary_key=True)]
            for column, column_spec in agent_config['monitoring'].items():
                columns.append(sa.Column(column, self.MAP_DB_TYPE[column_spec['db_type']]))
            self.metadata_controller[agent_name] = sa.Table(agent_name, self.metadata, *columns)

