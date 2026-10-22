"""Deterministic, auditable planning workflow, shared by web UI and MCP tools."""
from __future__ import annotations

import copy
import json
import math
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .catalog import DEFAULT_PANTRY, MEMBERS, PRODUCTS, RECIPES

DB_PATH = Path(os.environ.get('KINSHIP_DB', Path(__file__).resolve().parents[1] / 'kinship.db'))
_LOCK = threading.RLock()


def _initial_state() -> dict[str, Any]:
    return {'pantry': copy.deepcopy(DEFAULT_PANTRY), 'plan': None, 'shopping': [], 'tasks': [],
            'history': [], 'members': MEMBERS, 'budget': 20, 'last_updated': None}


def _db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.execute('CREATE TABLE IF NOT EXISTS household (id INTEGER PRIMARY KEY CHECK (id=1), state TEXT NOT NULL)')
    con.execute('INSERT OR IGNORE INTO household (id, state) VALUES (1, ?)', (json.dumps(_initial_state()),))
    con.commit()
    return con


def load() -> dict[str, Any]:
    with _LOCK, _db() as db:
        return json.loads(db.execute('SELECT state FROM household WHERE id=1').fetchone()[0])


def save(state: dict[str, Any]) -> None:
    state['last_updated'] = datetime.now(timezone.utc).isoformat()
    with _LOCK, _db() as db:
        db.execute('UPDATE household SET state=? WHERE id=1', (json.dumps(state),))
        db.commit()


def mutate(operation):
    """Serialize state read/modify/write within one process."""
    with _LOCK:
        state = load()
        result = operation(state)
        save(state)
        return result


def reset_demo() -> dict[str, Any]:
    with _LOCK:
        state = _initial_state()
        save(state)
        return {'message': 'Demo household restored to its starting state.', 'state': overview()}


def product_list() -> list[dict[str, Any]]:
    return [{'id': k, **v} for k, v in PRODUCTS.items()]


def available_recipes() -> list[dict[str, Any]]:
    return [{k: v for k, v in recipe.items() if k != 'steps'} for recipe in RECIPES]


def overview() -> dict[str, Any]:
    state = load()
    bought = sum(x['quantity'] * x['price'] for x in state['shopping'] if x['purchased'])
    remaining = sum(x['quantity'] * x['price'] for x in state['shopping'] if not x['purchased'])
    return {**state, 'products': product_list(), 'recipes': available_recipes(),
            'shopping_total': round(remaining, 2), 'bought_total': round(bought, 2),
            'tasks_pending': sum(not t['done'] for t in state['tasks']), 'currency': 'USD',
            'disclaimer': 'Demo prices are illustrative and do not represent live grocery prices.'}


def _estimate(recipe: dict, servings: int, pantry: dict) -> dict:
    factor = math.ceil(servings / 4)
    required = {k: v * factor for k, v in recipe['ingredients'].items()}
    missing = {k: max(0, q - int(pantry.get(k, 0))) for k, q in required.items()}
    missing = {k: q for k, q in missing.items() if q}
    price = round(sum(q * PRODUCTS[k]['price'] for k, q in missing.items()), 2)
    return {'recipe': recipe, 'required': required, 'missing': missing, 'cost': price,
            'pantry_used': sum(min(v, int(pantry.get(k, 0))) for k, v in required.items()),
            'total_needed': sum(required.values())}


def plan_meal(servings: int = 4, max_budget: float = 20.0, preference: str = 'vegetarian') -> dict:
    if not (1 <= servings <= 12):
        raise ValueError('servings must be between 1 and 12')
    if not (0 <= max_budget <= 1000):
        raise ValueError('max_budget must be between 0 and 1000')
    preference = preference.strip().lower()
    if preference not in ('vegetarian', 'any'):
        raise ValueError('This demo supports vegetarian or any preferences.')

    def operation(state):
        options = [_estimate(recipe, servings, state['pantry']) for recipe in RECIPES
                   if preference != 'vegetarian' or recipe['vegetarian']]
        affordable = [x for x in options if x['cost'] <= max_budget]
        # Within budget: maximize pantry reuse first, then prefer less money and faster cook time.
        # Without affordable option: pick closest shortfall and explicitly disclose it.
        if affordable:
            chosen = sorted(affordable, key=lambda x: (-x['pantry_used'], x['cost'], x['recipe']['minutes']))[0]
        else:
            chosen = sorted(options, key=lambda x: (x['cost'], -x['pantry_used']))[0]
        recipe = chosen['recipe']
        shopping = [{'id': item, 'name': PRODUCTS[item]['name'], 'icon': PRODUCTS[item]['icon'],
                     'unit': PRODUCTS[item]['unit'], 'price': PRODUCTS[item]['price'],
                     'quantity': quantity, 'purchased': False} for item, quantity in chosen['missing'].items()]
        # Tasks are persistent, fair assignments in a two-person household.
        steps = recipe['steps']
        tasks = [{'id': f'task-{i+1}', 'title': title, 'owner': state['members'][i % len(state['members'])],
                  'done': False} for i, title in enumerate(steps)]
        plan = {'recipe_id': recipe['id'], 'recipe_name': recipe['name'], 'emoji': recipe['emoji'],
                'minutes': recipe['minutes'], 'servings': servings, 'budget': max_budget,
                'estimated_spend': chosen['cost'], 'within_budget': chosen['cost'] <= max_budget,
                'pantry_used': chosen['pantry_used'], 'required': chosen['required'],
                'ingredient_count': len(chosen['required']), 'steps': steps,
                'reason': f"Used {chosen['pantry_used']} ingredient packages already at home. "
                          + (f"Estimated shopping stays within your ${max_budget:.2f} budget."
                             if chosen['cost'] <= max_budget else f"No candidate fits ${max_budget:.2f}; this is the least expensive option."),
                'alternatives': [{'name': x['recipe']['name'], 'cost': x['cost']} for x in
                                 sorted(options, key=lambda x: x['cost']) if x['recipe']['id'] != recipe['id']][:3]}
        state['plan'] = plan
        state['shopping'] = shopping
        state['tasks'] = tasks
        state['budget'] = max_budget
        state['history'] = ([{'action': 'plan_meal', 'recipe': recipe['name'], 'timestamp': datetime.now(timezone.utc).isoformat()}]
                            + state['history'])[:12]
        return {'message': f"I've planned {recipe['name']} for {servings}. "
                           f"You need {len(shopping)} shopping items, estimated ${chosen['cost']:.2f}. "
                           f"I also assigned {len(tasks)} cooking tasks to your household.",
                'plan': plan, 'shopping': shopping, 'tasks': tasks, 'workflow': ['Read household pantry',
                    'Compare five complete recipes', 'Check budget and pantry overlap',
                    'Generate exact missing-items shopping list', 'Split cooking tasks between household members']}
    return mutate(operation)


def add_pantry(item: str, quantity: int = 1) -> dict:
    item = item.strip().lower().replace(' ', '_').replace('-', '_')
    if item not in PRODUCTS:
        raise ValueError(f'Unknown pantry item: {item}. Use the list_products tool for valid ids.')
    if quantity < 1 or quantity > 50:
        raise ValueError('quantity must be from 1 to 50')
    def operation(state):
        state['pantry'][item] = state['pantry'].get(item, 0) + quantity
        return {'message': f"Added {quantity} {PRODUCTS[item]['unit']}(s) of {PRODUCTS[item]['name']} to pantry.",
                'item': item, 'quantity_now': state['pantry'][item]}
    return mutate(operation)


def mark_purchased(item: str) -> dict:
    item = item.strip().lower().replace(' ', '_').replace('-', '_')
    def operation(state):
        for shopping in state['shopping']:
            if shopping['id'] == item:
                if shopping['purchased']:
                    return {'message': f"{shopping['name']} was already marked purchased."}
                shopping['purchased'] = True
                state['pantry'][item] = state['pantry'].get(item, 0) + shopping['quantity']
                return {'message': f"Marked {shopping['name']} purchased and added {shopping['quantity']} to pantry."}
        raise ValueError(f'{item} not found on current shopping list')
    return mutate(operation)


def complete_task(task_id: str) -> dict:
    def operation(state):
        for task in state['tasks']:
            if task['id'] == task_id:
                task['done'] = True
                return {'message': f"Completed: {task['title']}", 'task': task}
        raise ValueError(f'Unknown task: {task_id}')
    return mutate(operation)


def household_brief() -> dict:
    state = overview()
    if not state['plan']:
        return {'message': 'No dinner plan yet. Ask me to plan a vegetarian dinner for four under $20.',
                'pantry_varieties': len(state['pantry']), 'budget': state['budget'], 'tasks_pending': 0}
    return {'message': f"Tonight: {state['plan']['recipe_name']} for {state['plan']['servings']}. "
                       f"${state['shopping_total']:.2f} left to buy; {state['tasks_pending']} cooking tasks pending.",
            'plan': state['plan'], 'shopping_remaining': [x for x in state['shopping'] if not x['purchased']],
            'tasks_pending': [x for x in state['tasks'] if not x['done']]}
