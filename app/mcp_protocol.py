"""Small, dependency-light MCP 2025-11-25 Streamable HTTP implementation.

Stateless JSON response mode (MCP-compatible), accepting POST JSON-RPC 2.0.
MCP endpoint intentionally binds through FastAPI and responds 405 on GET.
Only localhost origins accepted by default; configure MCP_ALLOWED_ORIGINS to deploy.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from . import engine

PROTOCOL_VERSION = '2025-11-25'
ROUTER = APIRouter()

def _schema(properties: dict, required: list[str] | None = None) -> dict:
    return {'type': 'object', 'properties': properties, 'required': required or [], 'additionalProperties': False}

SPEC = [
    ('household_brief', 'Read the current plan, unfinished cooking tasks and missing grocery items.', _schema({}), engine.household_brief),
    ('plan_dinner', 'Build an affordable dinner plan using pantry stock, shopping estimates and distributed tasks.',
      _schema({'servings': {'type': 'integer', 'minimum': 1, 'maximum': 12, 'default': 4},
               'max_budget': {'type': 'number', 'minimum': 0, 'maximum': 1000, 'default': 20},
               'preference': {'type': 'string', 'enum': ['vegetarian', 'any'], 'default': 'vegetarian'}}), engine.plan_meal),
    ('list_products', 'List valid grocery IDs and illustrative prices.', _schema({}), engine.product_list),
    ('list_recipes', 'List the recipe catalog with ingredient requirements.', _schema({}), engine.available_recipes),
    ('add_pantry_item', 'Increase quantity of a pantry item by product ID.',
      _schema({'item': {'type': 'string'}, 'quantity': {'type': 'integer', 'minimum': 1, 'maximum': 50, 'default': 1}}, ['item']), engine.add_pantry),
    ('mark_item_purchased', 'Mark a planned shopping item bought and add purchased units to pantry (no checkout or payment).',
      _schema({'item': {'type': 'string'}}, ['item']), engine.mark_purchased),
    ('complete_cooking_task', 'Mark an assigned cooking task completed.',
      _schema({'task_id': {'type': 'string'}}, ['task_id']), engine.complete_task),
    ('reset_demo', 'Reset fictional household data for repeatable demonstrations.', _schema({}), engine.reset_demo),
]
TOOLS = {entry[0]: entry for entry in SPEC}

def _response(msg_id: Any, result: Any = None, error: dict | None = None):
    return JSONResponse({'jsonrpc': '2.0', 'id': msg_id, **({'error': error} if error else {'result': result})})

def _err(msg_id: Any, code: int, message: str):
    return _response(msg_id, error={'code': code, 'message': message})

def _allowed(request: Request) -> bool:
    origin = request.headers.get('origin')
    if not origin:
        return True
    allowed = {o.strip() for o in os.environ.get('MCP_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',') if o.strip()}
    return origin in allowed

@ROUTER.post('/mcp')
async def post_mcp(request: Request):
    if not _allowed(request):
        return JSONResponse({'error': 'Forbidden origin'}, status_code=403)
    if 'application/json' not in request.headers.get('content-type', ''):
        return JSONResponse({'error': 'Expected application/json'}, status_code=415)
    accept = request.headers.get('accept', '')
    if 'application/json' not in accept or 'text/event-stream' not in accept:
        return JSONResponse({'error': 'Accept must include application/json and text/event-stream'}, status_code=406)
    token = os.environ.get('MCP_API_KEY')
    if token:
        import hmac
        if not hmac.compare_digest(request.headers.get('authorization', ''), f'Bearer {token}'):
            return JSONResponse({'error': 'Bearer token required'}, status_code=401)
    if int(request.headers.get('content-length', '0') or 0) > 128 * 1024:
        return JSONResponse({'error': 'Request too large'}, status_code=413)
    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _err(None, -32700, 'Parse error')
    if not isinstance(body, dict) or body.get('jsonrpc') != '2.0':
        return _err(body.get('id') if isinstance(body, dict) else None, -32600, 'Invalid Request')
    msg_id = body.get('id')
    method = body.get('method')
    header_ver = request.headers.get('mcp-protocol-version')
    if header_ver and header_ver != PROTOCOL_VERSION:
        return JSONResponse({'error': 'Unsupported MCP-Protocol-Version'}, status_code=400)
    if 'method' not in body or not isinstance(method, str):
        return _err(msg_id, -32600, 'Invalid Request')
    if msg_id is None:
        # MCP notifications get HTTP 202 with no content.
        if method.startswith('notifications/'):
            return Response(status_code=202)
        return _err(None, -32600, 'Request id required')
    args = body.get('params', {})
    if not isinstance(args, dict):
        return _err(msg_id, -32602, 'Parameters must be an object')
    if method == 'initialize':
        version = args.get('protocolVersion', PROTOCOL_VERSION)
        return _response(msg_id, {'protocolVersion': PROTOCOL_VERSION,
                                  'capabilities': {'tools': {'listChanged': False}},
                                  'serverInfo': {'name': 'kinship-household-copilot', 'version': '1.0.0'},
                                  'instructions': 'Plan family meals, shopping and cooking assignments with locally stored sample data.'})
    if method == 'ping':
        return _response(msg_id, {})
    if method == 'tools/list':
        return _response(msg_id, {'tools': [{'name': n, 'description': desc, 'inputSchema': schema}
                                            for n, desc, schema, fn in SPEC]})
    if method == 'tools/call':
        name = args.get('name')
        if name not in TOOLS:
            return _err(msg_id, -32602, 'Unknown tool')
        params = args.get('arguments', {})
        if not isinstance(params, dict):
            return _err(msg_id, -32602, 'Tool arguments must be an object')
        _, _, schema, fn = TOOLS[name]
        if set(params) - set(schema['properties']):
            return _err(msg_id, -32602, 'Unexpected tool arguments')
        if set(schema['required']) - set(params):
            return _err(msg_id, -32602, 'Missing required tool arguments')
        try:
            data = fn(**params)
            return _response(msg_id, {'content': [{'type': 'text', 'text': json.dumps(data, ensure_ascii=False)}],
                                      'structuredContent': {'result': data}, 'isError': False})
        except (ValueError, TypeError) as exc:
            return _response(msg_id, {'content': [{'type': 'text', 'text': str(exc)}], 'isError': True})
        except Exception:
            return _response(msg_id, {'content': [{'type': 'text', 'text': 'Internal tool failure'}], 'isError': True})
    return _err(msg_id, -32601, 'Method not found')

@ROUTER.get('/mcp')
async def get_mcp():
    return Response(status_code=405, headers={'Allow': 'POST'})
