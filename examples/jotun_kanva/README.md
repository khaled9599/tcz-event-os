# Jotun Kanva vertical slice

Proposes changing `KANVA-ENT-001` height from 4200 mm to 5500 mm. The change is recorded before mutation, cross-domain impact is inferred, approval is explicit, and the changed measurement becomes unverified until new evidence is supplied.
# Jotun KANVA Example

Run the canonical brain scenario:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --auto-approve-demo
```

This proves the brain can load a task graph from a project scenario, pause for L2/L3 approvals, resume with demo approvals, execute the pluggable runtime contract, judge outputs, and commit the proposed 5500mm entrance state.

Run the approval pause/resume flow:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --approval-file work/jotun_approvals.json
```

Edit `work/jotun_approvals.json` and change each decision from `pending` to `approved`, then resume:

```bash
python -m brain.runtime.cli --resume work/jotun_approvals.json
```
