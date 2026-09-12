# TCZ Agent Protocol

## Operating loop

`RECEIVE -> BUILD CONTEXT -> CHECK DEPENDENCIES -> ACCEPT/REJECT HANDOFF -> EXECUTE -> SELF-CHECK -> SUBMIT RESULT + EVIDENCE -> INDEPENDENT REVIEW -> APPROVAL GATE -> MUTATE STATE -> EMIT EVENT -> HANDOFF/CLOSE`

Every agent charter declares identity, mission, ownership, read/propose/mutate/approve permissions, prohibited actions, tools, knowledge packs, escalation rules and evaluation rubric.

`TaskEnvelope` carries objective, object IDs, inputs, constraints, outputs, acceptance criteria, dependencies and approval level.

`AgentResult` carries outputs, proposed mutations, artifacts, evidence-backed claims, assumptions, risks, issues and recommended next agents.

A downstream agent may reject an incomplete `HandoffEnvelope`.

The protocol is framework-independent. OpenAI Agents SDK, Pydantic AI, LangGraph or Temporal are runtime adapters, not the constitution.