from typing import List, TypedDict
from langgraph.graph import StateGraph


# Defining the state of the graph
class AgentState(TypedDict):
    values: List[int]
    name: str
    operation: str
    result: str

# Defining a node
def processor(state: AgentState) -> AgentState:
    """Function handles multiple operations"""

    result = -1
    if state['operation'] == '+':
        result = 1
        for i in state['values']:
            result *= i
    elif state['operation'] == '*':
        result = sum(state['values'])
    

    state['result'] = f"Hey {state['name']}, your result is {result}"

    return state

# Create graph
graph = StateGraph(AgentState)

# Adding nodes
graph.add_node("processor", processor)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

# Compiling the graph
app = graph.compile()

# Invoking the app
result = app.invoke({'name': 'John', 'values': [1,2,3,4,5], 'operation': "+"})
print(result)

result = app.invoke({'name': 'John', 'values': [1,2,3,4,5], 'operation': "*"})
print(result)