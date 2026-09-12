FIELD_IMPACT_RULES=[
("dimensions",{"spatial","blender","production_engineering","rigging","electrical","quantity","cost","schedule","visual_qa"}),
("av",{"av","rigging","electrical","show_control","content","cost"}),
("rigging",{"rigging","production_engineering","schedule","cost"}),
("electrical",{"electrical","av","lighting","show_control","hospitality"}),
("guest_count",{"hospitality","accessibility","operations","cost","schedule"}),
("vendor",{"vendor_management","procurement","cost","schedule"}),
("material",{"production_engineering","quantity","cost","vendor_management","visual_qa"})]
def infer_impact_domains(field_path):
    result=set(); n=field_path.lower()
    for token,domains in FIELD_IMPACT_RULES:
        if token in n: result|=domains
    return sorted(result or {"executive_producer"})
