import asyncio
import time

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure

from database import DBclient


class Plotter(object):

    def __init__(self, db_config, agents_config, loop=None):
        self.loop = loop
        self.db_config = db_config
        self.agents_config = agents_config

        self.clients = {}

        self.dbClient = DBclient(self.db_config, self.agents_config)
        self.figures = {}
        self.sources = {}
        self.stream = curdoc()
        if not loop:
            self.loop = asyncio.get_event_loop()

    def _create_sources(self):
        for agent, agent_config in self.agents_config.items():
            for data, data_config in agent_config['monitoring'].items():
                figure_name = '{agent}-{data}'.format(agent=agent, data=data)
                self.sources[figure_name] = {}
                self.sources[figure_name]['buffor'] = dict(x=[], y=[])
                source = ColumnDataSource(self.sources[figure_name]['buffor'])
                self.sources[figure_name]['source'] = source

    def _create_figures(self):
        for agent, agent_config in self.agents_config.items():
            for data, data_config in agent_config['monitoring'].items():
                figure_name = '{agent}-{data}'.format(agent=agent, data=data)
                fig = Figure(x_axis_type="datetime",
                             x_axis_label="Time",
                             y_axis_label=data_config['unit'],
                             title=figure_name)
                fig.line(source=self.sources[figure_name]['source'],
                         x='x',
                         y='y',
                         line_width=2,
                         alpha=.85,
                         color='red')
                self.figures[figure_name] = fig

    def _add_figures_to_stream(self):
        for figure in self.figures:
            self.stream.add_root(self.figures[figure])

    def featch_data_from_db(self):
        tasks = []
        for table in self.agents_config:
            tasks.append(self.dbClient.fetch_last_row(table_name=table))
        results = self.loop.run_until_complete(asyncio.gather(*tasks))
        return results

    def fill_buffors(self, results):
        for agent_info, result_list in zip(self.agents_config.items(), results):
            agent, agent_config= agent_info
            result = result_list[0]
            i = 1
            for data, data_config in agent_config['monitoring'].items():
                figure_name = '{agent}-{data}'.format(agent=agent, data=data)
                self.sources[figure_name]['buffor'] = dict(x=[result[0]], y=[result[1]])
                print(self.sources[figure_name]['buffor'])
                self.sources[figure_name]['source'].stream(self.sources[figure_name]['buffor'], 100)
                i += 1

    def streaming(self):
        data =self.featch_data_from_db()
        self.fill_buffors(data)
        # curdoc().add_periodic_callback(pull, 100)

from utils import parse_config

db_config, agents_config = parse_config('collector.ini')

P= Plotter(db_config, agents_config)
P._create_sources()
P._create_figures()
P._add_figures_to_stream()
P.featch_data_from_db()
data = P.featch_data_from_db()
P.fill_buffors(data)
P.stream.add_periodic_callback(P.streaming, 100)
# from utils import parse_config
# db_config, agents_config = parse_config('collector.ini')
# dbClient = DBclient(db_config, agents_config)
# def pull():
#     global loop, source, a
#     async def pulling_loop(interval=1):
#         global a
#         last_row = await dbClient.fetch_last_row(table_name='controler1')
#         data = last_row[0]
#         data_parsed = dict(x=[data[0]], y=[data[1]])
#         print(data_parsed)
#         source.stream(data_parsed, 100)
#         time.sleep(interval)
#         a += 1
#     loop.run_until_complete(pulling_loop())
# a = 0
#
# source = ColumnDataSource(dict(x=[], y=[]))
# fig = Figure(x_axis_type="datetime")
# fig.line(source=source, x='x', y='y', line_width=2, alpha=.85, color='red')
#
#
# loop = asyncio.get_event_loop()
# curdoc().add_root(fig)
#
# curdoc().add_periodic_callback(pull, 100)
# # pull()