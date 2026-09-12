from pydantic import BaseModel, Field
class ToolRecord(BaseModel):
    id:str; role:str; protocol:str|None=None; requires_api:bool=False; commercial_use_check:bool=True; mutates_external_state:bool=False; risk:str="medium"; fallback:str|None=None; outputs:list[str]=Field(default_factory=list)
DEFAULT_TOOL_CATALOG=[
ToolRecord(id="blender_mcp",role="3D scene execution",protocol="MCP",mutates_external_state=True,outputs=["blend","render"]),
ToolRecord(id="build123d_mcp",role="Parametric CAD",protocol="MCP",mutates_external_state=True,outputs=["STEP","STL","DXF","SVG"]),
ToolRecord(id="bonsai_mcp",role="BIM / IFC / quantity takeoff",protocol="MCP",mutates_external_state=True,outputs=["IFC","quantities","screenshots"]),
ToolRecord(id="blender_dmx",role="Event lighting visualization",outputs=["GDTF/MVR scene","lighting visualization"]),
ToolRecord(id="fspy",role="Camera matching",outputs=["camera calibration"]),
ToolRecord(id="colmap",role="Photogrammetry and camera reconstruction",outputs=["cameras","point cloud"]),
ToolRecord(id="rhino_grasshopper",role="Computational / NURBS design",mutates_external_state=True,outputs=["CAD geometry"]),
ToolRecord(id="nesting",role="Sheet/profile optimization",outputs=["DXF","cut list","waste report"])]
