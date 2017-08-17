import asyncio
from collections import defaultdict
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import column, row, gridplot
from bokeh.plotting import Figure

from database import DBclient


class Plotter(object):
    def __init__(self, db_config, agents_config, loop=None):
        self.loop = loop
        if not loop:
            self.loop = asyncio.get_event_loop()
        self.db_config = db_config
        self.agents_config = agents_config

        self.dbClient = DBclient(self.db_config, self.agents_config)
        self.figures = {}
        self.sources = {}
        self.stream = curdoc()

        self._create_sources()
        self._create_figures()
        self._add_figures_to_stream()

    def _create_sources(self):
        for agent, agent_config in self.agents_config.items():
            for data, data_config in agent_config['monitoring'].items():
                figure_name = '{agent}-{data}'.format(agent=agent, data=data)
                self.sources[figure_name] = {}
                # self.sources[figure_name]['buffor'] = dict(x=[], y=[])
                if data_config['db_type'] == 'json':
                    source = ColumnDataSource(dict(x=[], u=[], s=[], i=[]))
                else:
                    source = ColumnDataSource(dict(x=[], y=[]))
                self.sources[figure_name] = source

    def _create_figures(self):
        for agent, agent_config in self.agents_config.items():
            for data, data_config in agent_config['monitoring'].items():
                import time
                print(data_config)
                print(data)
                if data_config['db_type'] == 'json':
                    figure_name = '{agent}-{data}'.format(agent=agent, data=data)
                    fig = Figure(x_axis_type="datetime",
                                 x_axis_label="Time",
                                 y_axis_label=data_config['unit'],
                                 title=figure_name
                                 )
                    fig.title.text_font_size = '20pt'
                    fig.line(source=self.sources[figure_name],
                             x='x',
                             y='u',
                             legend="user",
                             line_width=3,
                             alpha=.5,
                             color='red')
                    fig.line(source=self.sources[figure_name],
                             x='x',
                             y='s',
                             legend="system",
                             line_width=3,
                             alpha=.5,
                             color='green')
                    fig.line(source=self.sources[figure_name],
                             x='x',
                             y='i',
                             legend="idle",
                             line_width=3,
                             alpha=.5,
                             color='blue')
                    self.figures[figure_name] = fig
                    continue
                figure_name = '{agent}-{data}'.format(agent=agent, data=data)
                fig = Figure(x_axis_type="datetime",
                             x_axis_label="Time",
                             y_axis_label=data_config['unit'],
                             title=figure_name
                             )
                fig.title.text_font_size = '20pt'
                fig.line(source=self.sources[figure_name],
                         x='x',
                         y='y',
                         line_width=3,
                         alpha=.5,
                         color='red')
                self.figures[figure_name] = fig

    def _add_figures_to_stream(self):
        figs = defaultdict(list)
        for figure in self.figures:
            host, figure_name = figure.split('-')
            figs[figure_name].append(self.figures[figure])
        grid = gridplot([figs[fig] for fig in figs])
        self.stream.add_root(grid)

    def featch_data_from_db(self):
        tasks = []
        for table in self.agents_config:
            tasks.append(self.dbClient.fetch_last_row(table_name=table))
        results = self.loop.run_until_complete(asyncio.gather(*tasks))
        return results

    def fill_buffors(self, results):
        for agent_info, result_list in zip(self.agents_config.items(), results):
            agent, agent_config = agent_info
            result = result_list[0]
            print(result)
            i = 1
            for data, data_config in agent_config['monitoring'].items():
                figure_name = '{agent}-{data}'.format(agent=agent, data=data)
                x = result[0]
                y = result[i]
                if isinstance(y, list):
                    self.sources[figure_name].stream(dict(x=[x], u=[y[0]], s=[y[1]], i=[y[2]]), 100)
                else:
                    self.sources[figure_name].stream(dict(x=[x], y=[y]), 100)
                i += 1

    def streaming(self):
        data = self.featch_data_from_db()
        print(data)
        self.fill_buffors(data)

    def run(self, periodic_time=1000):
        self.stream.add_periodic_callback(self.streaming, periodic_time)
