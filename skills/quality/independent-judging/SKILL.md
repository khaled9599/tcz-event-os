# Independent Judging

## Purpose
Evaluate specialist output independently against explicit acceptance criteria, blockers and evidence.

## Rules
1. Judge the submitted artifact, not the producer's confidence.
2. Read acceptance criteria before reading narrative justification.
3. Separate hard blockers from scored quality dimensions.
4. Require evidence for measurable claims.
5. Do not repair the artifact while judging it.
6. Return actionable findings tied to object IDs or output fields.
7. Use PASS only when all blockers clear and the required threshold is met.
8. Escalate ambiguous high-impact decisions instead of averaging them away.

## Default result
- verdict: PASS | REVISE | BLOCKED
- blocker_findings
- scored_dimensions
- evidence_gaps
- required_revisions
- confidence

## Bias controls
Use explicit rubrics, avoid rewarding verbosity, compare against canonical requirements, and keep the judge context independent from the specialist's hidden reasoning.

## Source synthesis
TCZ adaptation of LLM-as-judge, reflection and evaluator patterns from NeoLabHQ/context-engineering-kit and Agent-Skills-for-Context-Engineering.
