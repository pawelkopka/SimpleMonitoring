from utils import parse_config
from plotter import Plotter


db_config, agents_config = parse_config('collector.ini')
plotter = Plotter(db_config, agents_config)
plotter.run(800)


