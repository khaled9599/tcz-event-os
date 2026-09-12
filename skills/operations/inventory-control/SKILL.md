# Inventory Control

Track event assets through ownership, storage, reservation, issue, return and condition states.

## Asset classes
OWNED, RENTED, CONSUMABLE, CLIENT_OWNED, FABRICATED, DISPOSABLE.

## Procedure
- assign stable asset IDs
- record location, condition, quantity and project reservation
- prevent double allocation across overlapping projects
- capture check-out/check-in and damage status
- link rented assets to vendor/return deadlines
- link maintenance/calibration requirements where relevant

## Output
inventory_records, reservations, shortages, condition_issues, return_obligations, maintenance_flags.
