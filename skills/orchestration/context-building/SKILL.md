# Context Building

## Purpose
Construct the smallest authoritative context package that lets a specialist complete one task correctly.

## Retrieval order
1. Task object and target canonical object.
2. Locked requirements and latest approved version.
3. Direct dependencies and open issues.
4. Evidence supporting dimensions, costs, specs, materials, and decisions.
5. Only then retrieve historical lessons or external knowledge.

## Rules
- Prefer verified project truth over conversation history.
- Include source, status, version, and confidence for critical facts.
- Exclude unrelated event sections even when available.
- Distinguish VERIFIED, PROVISIONAL, ASSUMED, and UNKNOWN.
- Never hide a conflicting source. Surface the conflict and authority order.
- Large files remain references unless exact excerpts are required.

## Output contract
`ContextPackage` must include task_id, object_id, approved_state, constraints, dependencies, evidence_refs, unresolved_questions, prohibited_changes, allowed_tools, output_schema.

## Quality gate
A package fails if it omits a direct dependency, includes stale information as current truth, or fills a required unknown by inference.

## Source synthesis
Based on progressive disclosure, context isolation, filesystem context, and attention-budget principles reviewed from Agent-Skills-for-Context-Engineering and Context Engineering Kit.
