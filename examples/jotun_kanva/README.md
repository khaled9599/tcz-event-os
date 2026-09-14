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

Run only the impact task with the OpenAI-backed runtime:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --runtime openai-impact --approval-file work/jotun_openai_approvals.json
```

This mode requires the optional OpenAI SDK and `OPENAI_API_KEY`. It only replaces `T-IMPACT`; the remaining tasks use the deterministic runtime until each specialist adapter is promoted.

Save a full result for inspection:

```bash
python -m brain.runtime.cli --resume work/jotun_openai_approvals.json --output full --output-file work/jotun_openai_full_result.json
```

Run only the first impact-analysis phase:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --only-task T-IMPACT --output full --output-file work/impact_only_result.json
```

The deterministic `T-IMPACT` path returns affected domains, required agents, approval levels, risks, assumptions, recommended next tasks, and the entrance height delta without needing OpenAI credits.

Run impact plus spatial response:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --until-task T-SPATIAL --output full --output-file work/spatial_chain_result.json
```

Run through the production approval gate:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --until-task T-PRODUCTION --approval-file work/production_approvals.json
```

This pauses at L2 approval before executing the production review.

Run through the rigging safety gate:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --until-task T-RIGGING --approval-file work/rigging_approvals.json
```

This pauses with L2 and L3 approval packets before executing production and rigging reviews.

Run through the Blender production package:

```bash
python -m brain.runtime.cli examples/jotun_kanva/change_entrance_height.yaml --until-task T-BLENDER --approval-file work/blender_approvals.json
```

After approvals, this prepares a side-effect-free Blender package with the target height, scene actions, validation plan, and judge-ready evidence requirements.
