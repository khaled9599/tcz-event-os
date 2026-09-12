from tcz_event_os.protocols.contracts import ContextPackage
class ContextBuilder:
    def build(self,task,state):
        ids=set(task.object_ids); related=set(ids)
        for r in state.relations:
            if r.subject_id in ids: related.add(r.object_id)
            if r.object_id in ids: related.add(r.subject_id)
        auth={"project":state.project.model_dump(mode="json")}
        for name in ["venues","zones","installations","materials","assets","av_systems","rigging_systems","electrical_systems","hospitality_plans","accessibility_requirements","warehouse_items","vendors","costs","quantities"]:
            c=getattr(state,name); selected={k:v.model_dump(mode="json") for k,v in c.items() if k in related}
            if selected: auth[name]=selected
        return ContextPackage(task_id=task.id,project_id=task.project_id,target_object_ids=task.object_ids,authoritative_state=auth,dependencies=[r.model_dump(mode="json") for r in state.relations if r.subject_id in related or r.object_id in related],relevant_decisions=[d.model_dump(mode="json") for d in state.decisions.values() if related.intersection(d.affected_object_ids)],relevant_assumptions=[a.model_dump(mode="json") for a in state.assumptions.values() if related.intersection(a.affected_object_ids)],relevant_evidence=[e.model_dump(mode="json") for e in state.evidence.values() if related.intersection(e.supports_object_ids)],constraints=task.constraints,excluded_context_notes=["Unrelated project entities intentionally omitted."])
