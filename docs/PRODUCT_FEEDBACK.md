# Honest product feedback draft — edit after personal verification

**Tools actually used:** Public MCP protocol specification version 2025-11-25, Streamable HTTP / JSON-RPC; Python/FastAPI web tooling. The prototype was not built with gated Alexa+ Category SDK, CLI, Web Simulator or MCP Toolkit, and does not imply access to those systems.

### Which tools, APIs, SDKs did you use and why?

I used the public Model Context Protocol 2025-11-25 specification to expose household actions as a self-hosted Streamable HTTP MCP endpoint. The endpoint handles `initialize`, `tools/list`, `tools/call` and `ping`. FastAPI makes a web-facing demonstration possible alongside the MCP endpoint, with SQLite storing the household state.

### What worked well?

The public MCP protocol has a clear JSON-RPC message format and machine-readable tool schemas. A transport that can be exercised with standard HTTP requests makes it straightforward to test real tool discovery and calls without restricted hardware or private SDK access. The published hackathon FAQ explains that a self-hosted MCP plus a developer-built web simulator is acceptable.

### What needs improvement?

For independent hackathon developers, the distinction between a real MCP integration and gated Alexa+ preview tooling can be confusing. A single open-source runnable sample showing MCP 2025-11-25 initialization, tool discovery, authentication requirements and a simulated Alexa-like workflow would reduce onboarding friction. It would be helpful to have a clearly labeled public, nongated conformance test for Streamable HTTP.

### Onboarding experience

I could build and test a minimum MCP-compatible endpoint using only the public protocol specification and generic HTTP clients. The biggest learning curve was implementing and checking transport details: media types, version headers, id-based JSON-RPC requests, and notification responses. There was no access to restricted Alexa+ preview SDKs; a self-built simulator provided the UI demonstration.

### Would you build with it again?

**Yes, for MCP.** The standard gives a path from a small local prototype to a hosted tool integration, and it keeps domain logic separate from any one client. For a real Amazon Alexa+ deployment I would want broader access to the approved platform tools, device testing and per-household authorization before launching.

### Actionable feature request (optional)

**A public MCP 2025-11-25 reference conformance suite for Alexa+ candidates.** Priority: Important. A clear set of validation cases for initialize/discovery/tool invocation, headers, and failure behavior would help developers ship correct servers without access to private preview tooling.

### Factuality checklist

- [ ] I personally ran the MCP demo or tests before claiming this experience.
- [ ] I did **not** claim to have tested Alexa+ hardware or restricted developer tools.
- [ ] I verified each criticism/request reflects my actual usage.
- [ ] I did **not** report invented errors or frustration.
- [ ] I adjusted first-person language and account identity as needed.
