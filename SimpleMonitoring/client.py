from aiohttp import ClientSession
from urllib.parse import urljoin
import json
import aiohttp
import asyncio
import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)

class ClientAgent:
    """
    client for agent
    """
    logger = logging.getLogger('ClientAgent')

    def __init__(self, host: str, port: (str, int), loop=None):
        self.loop = loop
        self.url_perfix = 'http://{host}:{port}/'.format(host=host, port=port)

    async def _make_request_get(self, url: str, **kwargs):
        async with ClientSession(loop=self.loop) as session:
            async with session.get(url=urljoin(self.url_perfix, url), **kwargs) as resp:
                print(resp.url)
                # print(resp.raise_for_status())
                if resp.status != 200:
                    # print(resp.raise_for_status())
                    # self.logger.warning(resp.text)#TODO add logging error response
                    resp._body = None#TODO change repsone text to None
                    print(resp.text())
                    return resp
                return resp

    async def cpu_percent(self, interval=0, percpu=''):
        params = {'interval': str(interval), 'percpu': str(percpu)}
        print('cpu')
        resp = await self._make_request_get('cpu_percent', params=params)
        return json.loads(await resp.text())

    async def virtual_memory(self):
        print('memory')
        resp = await self._make_request_get('virtual_memory')
        return json.loads(await resp.text())

    async def sensors_temperatures(self):
        print('temp')
        resp = await self._make_request_get('sensors_temperatures')
        return json.loads(await resp.text())

    async def pid(self, name):
        params = {'name': name}
        resp = await self._make_request_get('pid', params=params)
        return json.loads(await resp.text())

if __name__ == '__main__':
      loop = asyncio.get_event_loop()
      a = ClientAgent('localhost', '8080', loop=loop)
      b = loop.run_until_complete(a.cpu_percent())
      print(b)
