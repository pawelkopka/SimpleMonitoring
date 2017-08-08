import psutil
from aiohttp import web
from typing import Dict, Any
Request = str  # TODO change it
Json = Dict[Any, Any]
Process = psutil.Process

class Agent(object):
    register = {} #name : p
### host

    def __init__(self):
        pass

    async def cpu_percent(self, request: Request) -> Json:
        """
        :param request:
        :return:
         json {'data': float or list floats}
        """
        query = request.rel_url.query
        return web.json_response(dict(data=psutil.cpu_percent(interval=float(query.get('interval', 0)),
                                                              percpu=bool(query.get('percpu', False)))),
                                 status=200)

    async def virtual_memory(self, request: Request) -> Json:
        """
        :param request: 
        :return:
         json {data: list(total, available, percent,
                          used, free, active, 
                          inactive, buffers, cached, 
                          shared)}
        """
        return web.json_response(dict(data=psutil.virtual_memory()))


    async def sensors_temperatures(self, request: Request) -> Json:
        """
        :param request: 
        :return:
         json {data: dict(dependd on hardware)}
        """
        return web.json_response(dict(data=psutil.sensors_temperatures()),
                                 status=200)

    async def _find_pid(self, process_name: str) -> (int or None):
        """
        
        :param request: 
        :return: 
            pid (int) or None
        """
        for proc in psutil.process_iter():
            try:
                process_info = proc.as_dict(attrs=['name', 'pid'])
                if process_info['name'].startswith(process_name):
                    return process_info['pid']
            except psutil.NoSuchProcess:
                return None

    async def pid(self, request: Request) -> (int or None):
        """
        :param request: 
        :return:
         pid (int) or None 404
        """
        query = request.rel_url.query
        if not 'name' in query:
            return web.json_response('Missing process name in query', status=404)
        pid = await self._find_pid(query['name'])
        if pid:
            return web.json_response(dict(data=pid), status=200)
        return web.json_response('Process {name} not founded'.format(name=query['name']), status=404)

    ### Process
    async def _process(self, pid: int) -> Process:
        """
        :param pid: 
        :return:
         Process (psutil object)
        """
        return psutil.Process(pid)

    async def _update_register(self, process_name):
        """
        :param process_name:  
        """
        if not process_name in self.register:
            pid = self._find_pid(process_name)
            if pid:
                self.register[process_name] = self._process(pid)

    # async def proc





