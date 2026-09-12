# Canonical Event Model

The Canonical Event Model is the single authoritative language used by every TCZ agent. Departmental views do not create separate truths.

## Three stores

- Canonical state: what is currently true about the project.
- Event history: what happened, in order, to produce that state.
- Knowledge/memory: what TCZ learned from previous projects and external references.

Agent chat history is not a source of truth.

## Entity families

Project/site: `Project`, `Client`, `Venue`, `Zone`, `Experience`.

Physical design: `Installation`, `Material`, `Asset`, dimensions, fabrication assemblies and artifact versions.

Technical systems: `AVSystem`, `RiggingSystem`, `ElectricalSystem`, `ShowCue`, lighting extensions.

Operations: `HospitalityPlan`, `AccessibilityRequirement`, guest/crowd and logistics extensions.

Supply chain: `Vendor`, `WarehouseItem`, procurement and rental records.

Commercial: `QuantityItem`, `CostItem`, forecast, committed and actual cost.

Governance: `Task`, `Risk`, `Issue`, `Assumption`, `Decision`, `ChangeRequest`, `Approval`, `Evidence`, `FileArtifact`.

## First-class relationships

`located_in`, `contains`, `depends_on`, `powered_by`, `rigged_by`, `controlled_by`, `supplied_by`, `fabricated_by`, `approved_by`, `costs_against`, `scheduled_for`, `references`, `affects`.

## Rules

1. Verified facts carry evidence.
2. Assumptions are explicit objects.
3. Approved decisions can be locked.
4. Agents propose mutations; protected state changes pass approval gates.
5. Accepted mutations emit domain events.
6. Files are versioned artifacts, not the canonical state itself.
7. Units are explicit.