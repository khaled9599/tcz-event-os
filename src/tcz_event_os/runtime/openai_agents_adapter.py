from tcz_event_os.agents.spec import AgentSpec
def render_instructions(spec:AgentSpec)->str:
    return f'''You are {spec.name} in TCZ Event OS.\nMission: {spec.mission}\nOwnership: {', '.join(spec.owns)}\nProhibited: {', '.join(spec.prohibited_actions)}\nRules: treat canonical context as project truth; never invent verified dimensions/capacities/costs/approvals; declare assumptions; return structured outputs; obey approval levels; escalate outside authority.'''
def build_openai_agent(spec,tools=None):
    try: from agents import Agent
    except ImportError as exc: raise RuntimeError("Install optional agents dependencies") from exc
    return Agent(name=spec.name,instructions=render_instructions(spec),tools=tools or [])
