import asyncio

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure

from collector import Collector




source = ColumnDataSource(dict(x=[], y=[]))
fig =Figure()
fig.line(source=source, x='x', y='y', line_width=2, alpha=.85, color='red')
a = 1
b = 0.1
def update():
    global a, b
    a+=1
    b+=0.2
    data = dict(x=[a], y=[b])
    source.stream(data, 100)


curdoc().add_root(fig)
curdoc().add_periodic_callback(update, 100)