# Material Takeoff

Convert approved geometry and fabrication logic into traceable quantity inputs.

## Procedure
1. Use the latest approved geometry/version only.
2. Measure area, length, count and volume from authoritative model data where available.
3. Separate net quantity from waste/allowance.
4. Record unit, source object, measurement method and confidence.
5. Keep finish quantities separate from structural/substrate quantities.
6. Flag provisional takeoffs when geometry is not frozen.
7. Recompute when a dependent dimension changes.

## Output
quantity_items with object_id, material, unit, net_qty, allowance, gross_qty, source, status.

Informed by Bonsai/IFC quantity takeoff and Rhino schedule/quantity workflows.
