# Render Validation

Validate that a render is evidence of the intended canonical state, not merely a polished image.

## Checks
- camera clearly shows the required object/relationship
- dimensions and proportions match current approved state
- materials/brand elements are traceable to approved sources
- no hidden geometry failures or obvious intersections
- venue/context is not misleading
- render version maps to model version

## Output
render_id, model_version, pass_fail, visual_findings, geometry_findings, evidence_refs, required_revisions.

Use a critic loop only until acceptance threshold is met or progress stalls.
