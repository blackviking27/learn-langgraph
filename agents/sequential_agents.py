from typing import TypedDict, List
from langgraph.graph import StateGraph

# Defining the state
class AgentState(TypedDict):
    name: str
    age: int
    skills: List[str]
    result: str

# Defining the node
def process_name(state: AgentState) -> AgentState:
    """This is the node which processes the node"""
    state["result"] = f"Hi {state['name']}"

    return state

def process_age(state:AgentState) -> AgentState:
    """This node processes the age of user"""

    state['result'] += f", you are {state['age']} years old!"

    return state

def process_skills(state: AgentState) -> AgentState:
    """This node will process the skill of user"""

    state['result'] += f"Your skills are:{','.join([ skill for skill in state['skills']])}"

    return state


# Setting the state

graph = StateGraph(AgentState)

# Adding node
graph.add_node('process_name', process_name)
graph.add_node('process_age', process_age)
graph.add_node('process_skills', process_skills)

# Adding connections
graph.set_entry_point('process_name')
graph.add_edge('process_name', 'process_age')
graph.add_edge('process_age', 'process_skills')
graph.set_finish_point('process_skills')

# Compile the graph
app = graph.compile()

result = app.invoke({'name': 'Steve', 'age': 40, 'skills': ['Python' , 'AI', 'Web']})

print(result)