"""Executable MCP 2025-11-25 client smoke test (stdlib only)."""
import json
import os
from urllib.request import Request, urlopen

URL = os.getenv('KINSHIP_MCP_URL', 'http://127.0.0.1:8000/mcp')
headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
           'MCP-Protocol-Version': '2025-11-25'}
if os.getenv('MCP_API_KEY'):
    headers['Authorization'] = 'Bearer ' + os.environ['MCP_API_KEY']

def request(identifier, method, params=None):
    data = {'jsonrpc': '2.0', 'id': identifier, 'method': method}
    if params is not None:
        data['params'] = params
    req=Request(URL,data=json.dumps(data).encode(),headers=headers,method='POST')
    with urlopen(req,timeout=15) as response:
        obj=json.load(response)
    print(f'\n# {method} (id={identifier})')
    print(json.dumps(obj,indent=2,ensure_ascii=False)[:3000])
    if 'error' in obj:
        raise RuntimeError(obj['error'])
    return obj

if __name__ == '__main__':
    request(1,'initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'kinship-smoke','version':'1.0'}})
    request(2,'tools/list')
    request(3,'tools/call',{'name':'plan_dinner','arguments':{'servings':4,'max_budget':15}})
    request(4,'tools/call',{'name':'household_brief','arguments':{}})
    print('\nAll MCP operations returned successfully.')
