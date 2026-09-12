# Blender Modeling

## Purpose
Produce safe, measurable Blender geometry from approved canonical dimensions and installation intent.

## Rules
1. Never invent dimensions. Missing dimensions are issues, not creative freedom.
2. Work in real units and verify scene scale before modeling.
3. Build from primary masses to secondary structure to detail.
4. Apply transforms deliberately and keep object naming tied to canonical IDs.
5. Prefer procedural/parametric construction where revisions are expected.
6. Save versioned checkpoints before destructive changes.
7. Validate bounds, intersections, normals, transforms, and object connectivity before render/export.
8. Attach evidence renders and measured bounds to the result.

## Output contract
- blend artifact/version
- object-to-canonical-ID map
- measured bounds
- validation findings
- render evidence
- assumptions and unresolved geometry issues

## Source synthesis
Adapted for event production from arjun988/blender-skills, TMHSDigital/Blender-Developer-Tools and RobLe3/cc-blender-skill. No upstream code is vendored here.
