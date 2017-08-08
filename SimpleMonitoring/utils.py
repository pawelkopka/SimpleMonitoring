import os
import configparser

def parse_config(config_path='collector.ini'):
    general = ['database']
    path = os.path.dirname(os.path.realpath(__file__))  # TODO change arg path
    path = os.path.join(path, config_path)
    config = configparser.ConfigParser()
    config.sections()
    config.read(path)
    db_config = dict(config.items('database'))
    agents_config = {}
    for section in config.sections():
        if section not in general:
            agents_config[section] = dict(config.items(section))
            try:
                monitoring = agents_config[section].pop('monitoring')
                monitoring = monitoring.split()
                monitoring_type = agents_config[section].pop('monitoring_type')
                monitoring_type = monitoring_type.split()
                monitoring_unit = agents_config[section].pop('monitoring_unit')
                monitoring_unit = monitoring_unit.split()
            except KeyError:
                print('Nothing to monitoring in config')  # TODO change to logging

            agents_config[section]['monitoring'] = dict()
            for name, db_type, unit in zip(monitoring, monitoring_type, monitoring_unit):
                agents_config[section]['monitoring'][name] = dict(db_type=db_type, unit=unit)

    return db_config, agents_config
