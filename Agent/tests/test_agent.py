import pytest
import json
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))



from main import create_app
from psutil import Process
def json_parser(text: str) -> dict:
    return json.loads(text)

###Request
async def test_cpu_percent(test_client):
    client = await test_client(create_app)
    resp = await client.get('/cpu_percent')
    assert resp.status == 200
    text = await resp.text()
    data = json_parser(text)
    assert isinstance(data, dict)
    assert data.keys() == {'data'}
    assert isinstance(data['data'], float)

async def test_cpu_percent_query_interval(test_client):
    client = await test_client(create_app)
    resp = await client.get('/cpu_percent?interval=0.01')
    assert resp.status == 200
    text = await resp.text()
    data = json_parser(text)
    assert isinstance(data, dict)
    assert data.keys() == {'data'}
    assert isinstance(data['data'], float)


async def test_cpu_percent_query_percpu(test_client):
    client = await test_client(create_app)
    resp = await client.get('/cpu_percent?percpu=True')
    assert resp.status == 200
    text = await resp.text()
    data = json_parser(text)
    assert isinstance(data, dict)
    assert data.keys() == {'data'}
    assert isinstance(data['data'], list)
    assert isinstance(data['data'][0], float)

async def test_cpu_percent_query_percpu_interval(test_client):
    client = await test_client(create_app)
    resp = await client.get('/cpu_percent?percpu=True&interval=0.01')
    assert resp.status == 200
    text = await resp.text()
    data = json_parser(text)
    assert isinstance(data, dict)
    assert data.keys() == {'data'}
    assert isinstance(data['data'], list)
    assert isinstance(data['data'][0], float)

async def test_virtual_memory(test_client):
    client = await test_client(create_app)
    resp = await client.get('/virtual_memory')
    assert resp.status == 200
    text = await resp.text()
    data = json_parser(text)
    assert isinstance(data, dict)
    assert data.keys() == {'data'}
    assert isinstance(data['data'], list)
    for element in data['data']:
        assert isinstance(element, (int, float))

async def test_sensors_temperatures(test_client):
    client = await test_client(create_app)
    resp = await client.get('/sensors_temperatures')
    assert resp.status == 200
    text = await resp.text()
    data = json_parser(text)
    assert isinstance(data, dict)
    assert data.keys() == {'data'}
    assert isinstance(data['data'], dict)
    assert isinstance(data['data']['coretemp'], list)

async def test_pid_no_query(test_client):
    client = await test_client(create_app)
    resp = await client.get('/pid')
    assert resp.status == 404
    text = await resp.text()
    assert 'Missing process name in query'in text

async def test_pid_non_existing_process(test_client):
    client = await test_client(create_app)
    resp = await client.get('/pid?name=Ty_durniu')
    assert resp.status == 404
    text = await resp.text()
    assert 'Process Ty_durniu not founded'in text

async def test_pid_existing_process(test_client):
    client = await test_client(create_app)
    resp = await client.get('/pid?name=pytest')
    assert resp.status == 200
    text = await resp.text()
    data = json_parser(text)
    assert isinstance(data, dict)
    assert isinstance(data['data'], int)

#TODO add test private func like _find_pid or _process
#TODO add fake process and get it pid