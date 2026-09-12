# Runtime Architecture

MVP: Pydantic models + JSON/SQLite/PostgreSQL + agent runtime adapter + deterministic gates.

Production: add Temporal for long-lived workflows, waits, resumability, approvals and replayable execution.

Tool layer: prefer MCP adapters for Blender, build123d, Bonsai/IFC, Rhino and other specialist tools.

Event layer: persist append-only domain events. Add an event bus only when asynchronous subscribers justify it.

Do not couple the Canonical Event Model to one agent framework.