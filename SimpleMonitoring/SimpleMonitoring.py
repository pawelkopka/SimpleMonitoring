from collector import Collector
from utils import parse_config

db_config, agents_config = parse_config('collector.ini')

bone_colletor = Collector(db_config, agents_config)
bone_colletor.initialization_clients()
bone_colletor.loop.run_until_complete(bone_colletor.task_scheduler(interval=3))

