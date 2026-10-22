"""Kinship demo app and standards-compliant MCP Streamable HTTP endpoint."""
from __future__ import annotations
import os
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from . import engine
from .catalog import PRODUCTS
from .mcp_protocol import ROUTER, PROTOCOL_VERSION

HERE = Path(__file__).resolve().parents[1]
app = FastAPI(title='Kinship · household co-pilot', version='1.0.0',
              description='A stateful voice-first household planner and MCP 2025-11-25 server.')
app.include_router(ROUTER)
app.mount('/static', StaticFiles(directory=HERE / 'static'), name='static')

class Message(BaseModel):
    text: str = Field(min_length=1, max_length=500)

class PlanRequest(BaseModel):
    servings: int = Field(default=4, ge=1, le=12)
    max_budget: float = Field(default=20.0, ge=0, le=1000)
    preference: str = 'vegetarian'

class PantryRequest(BaseModel):
    item: str
    quantity: int = Field(default=1, ge=1, le=50)

@app.get('/')
def home():
    return FileResponse(HERE / 'static' / 'index.html')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'service': 'kinship', 'mcp_version': PROTOCOL_VERSION, 'transport': 'streamable-http'}

@app.get('/api/state')
def state():
    return engine.overview()

@app.get('/api/brief')
def brief():
    return engine.household_brief()

@app.post('/api/plan')
def plan(body: PlanRequest):
    try:
        return engine.plan_meal(body.servings, body.max_budget, body.preference)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post('/api/pantry')
def pantry(body: PantryRequest):
    try:
        return engine.add_pantry(body.item, body.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post('/api/shopping/{item}/purchased')
def purchased(item: str):
    try:
        return engine.mark_purchased(item)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.post('/api/tasks/{task_id}/complete')
def task_complete(task_id: str):
    try:
        return engine.complete_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.post('/api/reset')
def reset():
    return engine.reset_demo()


def respond_to_text(text: str) -> dict:
    """Transparent task-oriented voice command dispatcher; not an LLM or Amazon SDK."""
    q = text.lower().strip().rstrip('?.!')
    if any(key in q for key in ('plan', 'cook', 'dinner', 'meal', 'feed', 'make tonight')):
        people = re.search(r'\b(?:for|serve|serves|feeding)\s+(\d{1,2})(?:\s+(?:people|guests|persons))?\b', q)
        money = re.search(r'\b(?:under|below|budget(?:\s+of)?|for less than)\s*\$?\s*(\d+(?:\.\d{1,2})?)\b', q)
        dollars = re.search(r'\$\s*(\d+(?:\.\d{1,2})?)', q)
        servings = int(people.group(1)) if people else 4
        budget = float((money or dollars).group(1)) if (money or dollars) else 20.0
        try:
            return engine.plan_meal(servings, budget)
        except ValueError as exc:
            return {'message': str(exc), 'error': True}
    if any(key in q for key in ('brief', 'status', "what's next", 'what is next', 'remaining', 'what do we need', 'update')):
        return engine.household_brief()
    if 'recipe' in q or 'menu' in q:
        recipes = engine.available_recipes()
        return {'message': 'I can choose from: ' + ', '.join(r['name'] for r in recipes) + '. Ask me to plan dinner to generate a shopping list and tasks.',
                'recipes': recipes}
    if q.startswith(('bought ', 'purchased ', 'mark bought ')):
        for item in PRODUCTS:
            if item.replace('_', ' ') in q or PRODUCTS[item]['name'].lower() in q:
                try:
                    return engine.mark_purchased(item)
                except ValueError as exc:
                    return {'message': str(exc), 'error': True}
    if q.startswith(('add ', 'stock ')):
        for item in PRODUCTS:
            if item.replace('_', ' ') in q or PRODUCTS[item]['name'].lower() in q:
                match = re.search(r'\b(\d{1,2})\b', q)
                try:
                    return engine.add_pantry(item, int(match.group(1)) if match else 1)
                except ValueError as exc:
                    return {'message': str(exc), 'error': True}
    if 'done' in q or 'complete task' in q:
        match = re.search(r'(?:task[- ]?)(\d+)', q)
        if match:
            try:
                return engine.complete_task('task-' + match.group(1))
            except ValueError as exc:
                return {'message': str(exc), 'error': True}
    if 'reset' in q:
        return engine.reset_demo()
    return {'message': 'I can plan a dinner, coordinate groceries, and track cooking tasks. Try “Plan vegetarian dinner for 4 under $15” or “What is left to do?”',
            'help': True}

@app.post('/api/message')
def message(body: Message):
    return respond_to_text(body.text)
