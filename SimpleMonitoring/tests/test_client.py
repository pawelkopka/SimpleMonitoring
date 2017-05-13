import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
print(sys.path)
from aiohttp.test_utils import loop_context, TestClient
import asyncio
import pytest
from aiohttp import web
from client import ClientAgent
from Agent.main import create_app
import Agent.agent

@pytest.fixture() #need running app TODO change it to automation
def client():
    return ClientAgent('127.0.0.1', '8080')

async def test_cpu_percent(client):
    out = await client.cpu_percent()
    assert isinstance(out, dict)
    assert 'data' in out
    assert isinstance(out['data'], float)

async def test_cpu_percent_with_args(client):
    out = await client.cpu_percent(interval=0.1, percpu=True)
    assert isinstance(out, dict)
    assert 'data' in out
    assert isinstance(out['data'], list)
    assert isinstance(out['data'][0], float)

async def test_virtual_memory(client):
    out = await client.virtual_memory()
    assert isinstance(out, dict)
    assert 'data' in out
    assert isinstance(out['data'], list)
    for element in out['data']:
        assert isinstance(element, (int, float))
        
async def test_sensors_temperatures(client):
    out = await client.sensors_temperatures()
    assert isinstance(out, dict)
    assert 'data' in out
    assert isinstance(out['data'], dict)
    assert isinstance(out['data']['coretemp'], list)

async def test_pid_non_existing_process(client):
    out = await client.pid('Ty_durniu')
    assert out == None

async def test_pid_existing_process(client):
    out = await client.pid('pytest')
    assert isinstance(out, dict)
    assert 'data' in out
    assert isinstance(out['data'], int)
