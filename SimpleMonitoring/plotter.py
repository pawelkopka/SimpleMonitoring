#test plot
import asyncio
import time

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure

from database import DBclient

dbc = DBclient()

def pull():
    global loop, source, a
    async def pulling_loop(interval=1):
        global a
        last_row = await dbc.fetch_last_row(table_name='controler1')
        data = last_row[0]
        data_parsed = dict(x=[data[0]], y=[data[1]])
        print(data_parsed)
        source.stream(data_parsed, 100)
        time.sleep(interval)
        a += 1
    loop.run_until_complete(pulling_loop())
a = 0

source = ColumnDataSource(dict(x=[], y=[]))
fig = Figure(x_axis_type="datetime")
fig.line(source=source, x='x', y='y', line_width=2, alpha=.85, color='red')


loop = asyncio.get_event_loop()
curdoc().add_root(fig)

curdoc().add_periodic_callback(pull, 100)
pull()