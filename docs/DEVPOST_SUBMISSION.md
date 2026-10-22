# Devpost entry — ready to edit and paste

**Project name:** Kinship — More Living, Less Juggling  
**Primary track:** Alexa+  
**Short pitch:** A voice-first, MCP-powered household co-pilot that transforms one dinner request into a realistic plan, the groceries you actually need, and fairly assigned cooking tasks.

## Inspiration

Home life is full of tiny decisions. Planning a family meal can require separate apps for recipe ideas, checking what is in the cupboard, calculating the cost, and sharing work. Kinship proposes a simpler interaction: tell your home what you want, and let connected tools coordinate the details.

## What it does

Kinship is a small, fully runnable, Alexa+-inspired household assistant. Ask, “Plan a vegetarian dinner for four under $15,” and it reads the fictional household pantry, compares five recipes, selects a feasible dinner with a transparent scoring heuristic, calculates missing ingredients and sample prices, and assigns preparation steps to two family members. The result appears immediately in a polished, interactive dashboard. Mark groceries purchased or tasks completed, reload the page, and the household brief reflects the changes.

The primary integration surface is an **actual self-hosted MCP server** at `POST /mcp`, supporting the MCP `2025-11-25` protocol over Streamable HTTP. Eight discoverable tools expose the same planning and state-changing actions to compatible MCP clients. A responsive browser UI simulates the sort of experience someone might have with a voice-first household co-pilot; no restricted Alexa+ developer tools or physical device are claimed.

## How we built it

A FastAPI Python backend serves the application and implements a JSON-RPC 2.0 MCP endpoint. SQLite stores household context across sessions. The planning engine evaluates locally supplied example recipes using per-ingredient pantry quantities and transparent illustrative costs; it ranks within-budget recipes by pantry reuse, then cost and preparation time. A single orchestration call builds the meal plan, produces a draft shopping list, and allocates cooking steps. The browser simulator is vanilla JavaScript and CSS. Browser speech recognition can be used where supported, or commands can be typed.

The code includes automated tests for the complete REST planning/purchasing/task lifecycle and for MCP initialization, discovery, tool invocation, invalid version headers, origin checks, and optional bearer authorization. No external API keys or live user accounts are required to run the prototype.

## Challenges

The key design challenge was balancing an intuitive conversational interface with a reproducible, verifiable MCP protocol. The prototype separates a deliberately narrow browser intent dispatcher from real structured MCP tools, and exposes its decision reasoning and estimated spend instead of pretending to use an LLM or live retailer integration.

## Accomplishments

- Real MCP 2025-11-25 Streamable HTTP endpoint and eight callable tools.
- One request coordinates pantry check, recipe selection, budget check, shopping list, and task handoff.
- Browser-facing command flow and responsive dashboard are backed by persistent SQLite state.
- Fully reproducible local or Docker deployment and automated integration tests.
- No special Alexa+ preview access, grocery credentials, payments, or API keys needed.

## What we learned

A good voice-first integration is more than a Q&A bot: it needs durable context, explicit tool boundaries, predictable failure behavior, and visible results in the world. A useful demo should expose what the automation did, why it chose a result, and what the human remains in control of.

## What's next

For real-world deployment: integrate permissioned user accounts, per-household separation, real grocery/catalog providers with permission, optional LLM-driven intent parsing, and approved Alexa+ add-on access when generally available. The current app intentionally uses fictional demo data and does **not** order groceries.

## Submission fields to fill manually

- **Project repository:** `https://github.com/<YOUR_USERNAME>/kinship-alexa-mcp` (replace only after publishing)
- **Public YouTube/Vimeo demo:** `<UPLOAD_VIDEO_AND_PASTE_PUBLIC_URL>`
- **Built with:** Python, FastAPI, SQLite, JSON-RPC 2.0, MCP 2025-11-25 Streamable HTTP, HTML, CSS, JavaScript, pytest, Docker
- **Product feedback:** Use `docs/PRODUCT_FEEDBACK.md` as an editable starting point; describe only testing you personally confirmed.
- **Optional website link:** your deployed instance (leave blank if not deployed)

**Important:** Read and adapt this text after running the project yourself. Ensure that all claims are accurate and consistent with your entrant ownership and the official hackathon rules. Do not claim AWS Builder or the Open Source mini challenge unless you meet their **additional** requirements.
