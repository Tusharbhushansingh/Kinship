# Hackathon judge Q&A — Kinship

**Is there a compulsory presentation or interview?** According to the official 2026 Devpost rules, none is scheduled for every entrant. Judges generally review the source repository, project narrative, demo and product feedback. Verification of a possible winner's identity, qualifications and personal role may happen.

## Questions you should be able to answer truthfully

**Q: What problem does Kinship solve?**
A: It coordinates several small household decisions: choosing dinner within a budget, reusing what's in the pantry, identifying missing groceries and tracking assigned tasks.

**Q: Why MCP?**
A: It exposes the household workflows as discoverable tools, so a compatible AI client can call them without depending on the webpage's REST interface.

**Q: How does it work?**
A: A FastAPI app serves the dashboard and MCP endpoint. `app/engine.py` holds the planning and persistence logic; `app/catalog.py` holds sample recipes and prices; SQLite stores pantry, shopping and task state. `app/mcp_protocol.py` implements JSON-RPC tool discovery and invocation.

**Q: Is it an actual Alexa skill or integrated with Alexa+?**
A: No. It's a self-hosted MCP server with an Alexa+-inspired browser simulator. This matches the route the hackathon allows, but we have not connected to actual Alexa hardware.

**Q: Is it generative AI?**
A: Not presently. The demo parses a small set of instructions and uses deterministic planning and predefined recipes; the MCP interface is compatible with an external agent, but no LLM is included in the current runtime.

**Q: Do grocery prices come from Amazon or the web?**
A: No. They're sample prices inside the project's catalog. Kinship doesn't buy anything.

**Q: Does the plan survive a browser reload?**
A: Yes, state is persisted in SQLite.

**Q: What did you personally do?**
A: Prepare your own factual response. The initial prototype was generated with ChatGPT assistance. Review, test and modify the code yourself and describe your actual contributions accurately. Do not claim you wrote code that you have not written.

**Q: What would you build next?**
A: Add a proper agent orchestration layer, authentication and multiple households, live opt-in retailer prices and tested Alexa+ integration as access permits.

**Q: What's the key differentiator?**
A: One action coordinates meal selection, pantry awareness, price estimates, shopping and tasks; the MCP tools preserve household state between steps.

## Dates and source

Official rules: https://amazonappdev2026.devpost.com/rules
Submission deadline: Oct 23, 2026 12pm Pacific (Oct 24, 2026 12:30am IST).
Judging: Nov 9–20, 2026 (Pacific dates).
Winners: on or around Dec 3, 2026.
