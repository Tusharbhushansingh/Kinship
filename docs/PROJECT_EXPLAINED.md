# Kinship explained simply

## The idea

Kinship is a household co-pilot demo. It answers a practical request like "Plan a vegetarian dinner for four people for less than $15" and also coordinates the steps needed to carry out that dinner plan.

## The five things that happen after a request

1. **Read the pantry:** How much food is already at home?
2. **Compare recipes:** Consider five demo recipes and their ingredient requirements.
3. **Check the budget:** Determine which recipes can be made with the fewest additional purchases, favoring reuse of pantry items.
4. **Create a shopping list:** List only the missing ingredients, with illustrative sample prices.
5. **Assign tasks:** Split preparation tasks across Alex and Sam, two *fictional* household members.

The browser then lets you tick groceries as purchased and tasks as completed. All changes save in a local SQLite database. Refreshing the page preserves the state. Nothing is bought in the real world.

## Why it is an MCP project

MCP, Model Context Protocol, is a standardized way for an AI application or other MCP client to discover and call capabilities provided by a server. Kinship publishes eight such capabilities as JSON-RPC tools on `POST /mcp`: `household_brief`, `plan_dinner`, `list_products`, `list_recipes`, `add_pantry_item`, `mark_item_purchased`, `complete_cooking_task`, and `reset_demo`.

That makes it possible for a compatible external client to call the same functionality as the browser. The included browser uses normal FastAPI REST endpoints. The website is an **Alexa+-inspired simulation only**, not a real Alexa integration. The current natural-language parser is rule-based, **not generative AI**.

## Technical building blocks

- **FastAPI (`app/main.py`):** Receives browser requests and serves the web app.
- **MCP protocol (`app/mcp_protocol.py`):** Handles MCP JSON-RPC requests and tool discovery/calls.
- **Planning engine (`app/engine.py`):** Calculates missing items and meal preferences, divides tasks, persists changes.
- **Sample catalog (`app/catalog.py`):** Contains demo recipes, pantry products and example prices.
- **SQLite (`kinship.db`):** Stores the demo household's current information.
- **HTML/CSS/JavaScript (`static/`):** Shows the web dashboard and optional browser speech recognition.
- **Tests (`tests/`):** Verify core REST and MCP flows; run with `python -m pytest -q`.

## Laptop quick start (Windows)

1. Install Python 3.10 or newer.
2. Unzip project and open a terminal in `kinship-alexa-mcp`.
3. Run `py -m venv .venv`.
4. Run `.venv\Scripts\activate` from Command Prompt (PowerShell uses `.venv\Scripts\Activate.ps1`).
5. Run `python -m pip install -r requirements.txt`.
6. Run `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
7. Visit `http://127.0.0.1:8000` in your browser.

Do **not** claim that Alexa or an LLM is connected, that grocery prices are live, or that a real purchase happens. Review the hackathon rules and describe the code and contributions accurately in your submission.
