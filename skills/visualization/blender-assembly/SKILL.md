# Blender Assembly

## Purpose
Ensure event installations are modeled as connected assemblies rather than disconnected visual masses.

## Procedure
1. Build a connection map before geometry creation: part, parent, contact face, overlap/joint, fastener or support assumption.
2. Model primary frame first, then secondary frame, substrate, scenic finish, branding mounts and service interfaces.
3. For beams/rails/pipes between points, derive length and orientation from endpoints rather than eyeballing Euler rotations.
4. Measure world-space bounds after important steps.
5. Verify required overlaps/contact and flag impossible intersections.
6. Apply transforms intentionally and audit scale/rotation before handoff.
7. Keep every assembly component traceable to a canonical object or child component ID.

## Output contract
connection_map, component_list, measured_bounds, overlap_checks, transform_audit, unresolved_connections.

## Source synthesis
TCZ adaptation of ProfRino/Blender-MCP-Assembly-Skill connection planning, measurement and transform-audit principles.
