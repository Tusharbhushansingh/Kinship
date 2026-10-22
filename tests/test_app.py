"""End-to-end ASGI API tests including actual MCP 2025-11-25 method sequence."""
from __future__ import annotations
import json
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app import engine

@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, 'DB_PATH', tmp_path / 'test.db')
    engine.reset_demo()

@pytest.mark.anyio
async def test_end_to_end_household_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        health = await client.get('/api/health')
        assert health.status_code == 200
        assert health.json()['mcp_version'] == '2025-11-25'
        response = await client.post('/api/message', json={'text': 'Plan vegetarian dinner for 4 under $15'})
        assert response.status_code == 200
        result=response.json()
        assert result['plan']['servings'] == 4
        assert result['plan']['within_budget']
        assert next(a for a in result['plan']['alternatives'] if a['name']=='Golden potato & egg skillet')['cost'] > 0
        assert result['workflow'][-1] == 'Split cooking tasks between household members'
        state=(await client.get('/api/state')).json()
        assert state['plan']['recipe_id'] == 'chickpea-curry'
        assert len(state['shopping']) == 2
        assert {i['id'] for i in state['shopping']} == {'chickpeas','coconut_milk'}
        assert state['tasks_pending'] == 3
        assert state['shopping_total'] == 4.10
        purchased = await client.post('/api/shopping/coconut_milk/purchased')
        assert purchased.status_code == 200
        assert (await client.get('/api/state')).json()['shopping_total'] == 1.45
        task = await client.post('/api/tasks/task-1/complete')
        assert task.status_code == 200
        assert (await client.get('/api/state')).json()['tasks_pending'] == 2
        brief=(await client.get('/api/brief')).json()
        assert '2 cooking tasks' in brief['message']
        assert len(brief['tasks_pending']) == 2
        assert (await client.post('/api/reset')).status_code == 200
        assert (await client.get('/api/state')).json()['plan'] is None

@pytest.mark.anyio
async def test_budget_and_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response=await client.post('/api/plan',json={'servings':12,'max_budget':0.25})
        assert response.status_code == 200
        assert response.json()['plan']['within_budget'] is False
        assert 'No candidate fits' in response.json()['plan']['reason']
        invalid=await client.post('/api/plan',json={'servings':30})
        assert invalid.status_code == 422
        invalid2=await client.post('/api/pantry',json={'item':'not_product','quantity':1})
        assert invalid2.status_code == 422

@pytest.mark.anyio
async def test_mcp_transport_tools_and_security(monkeypatch):
    headers={'content-type':'application/json','accept':'application/json, text/event-stream',
             'MCP-Protocol-Version':'2025-11-25'}
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        async def call(method, params=None, id=1):
            data={'jsonrpc':'2.0','id':id,'method':method}
            if params is not None:data['params']=params
            return await client.post('/mcp',headers=headers,json=data)
        init=await call('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'pytest','version':'1'}})
        assert init.status_code == 200
        assert init.json()['result']['protocolVersion'] == '2025-11-25'
        note=await client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','method':'notifications/initialized'})
        assert note.status_code == 202
        tools=(await call('tools/list')).json()['result']['tools']
        assert any(t['name']=='plan_dinner' for t in tools)
        plan=(await call('tools/call', {'name':'plan_dinner','arguments':{'servings':4,'max_budget':15}})).json()
        assert plan['result']['isError'] is False
        data=json.loads(plan['result']['content'][0]['text'])
        assert data['plan']['within_budget']
        assert (await client.get('/mcp')).status_code == 405
        assert (await client.post('/mcp',headers={**headers,'Origin':'https://evil.example'},json={'jsonrpc':'2.0','id':1,'method':'ping'})).status_code==403
        assert (await client.post('/mcp',headers={**headers,'MCP-Protocol-Version':'2024-11-05'},json={'jsonrpc':'2.0','id':1,'method':'ping'})).status_code==400
        monkeypatch.setenv('MCP_API_KEY','testing-secret')
        assert (await call('ping')).status_code == 401
        secured = await client.post('/mcp',headers={**headers,'Authorization':'Bearer testing-secret'},json={'jsonrpc':'2.0','id':1,'method':'ping'})
        assert secured.status_code==200
        assert secured.json()['result']=={}
