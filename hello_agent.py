from typing import Dict, TypedDict
from langgraph.graph import StateGraph


# Creating a agent state
# This is the state schema
class AgentState(TypedDict):
    message: str

# Creating a node
def compliment_node(state: AgentState) -> AgentState:
    """Simple node that adds a positive message to the state"""

    state['message'] = f"Hey {state['message']}, great job out there"

    return state

# Creating the graph
graph = StateGraph(AgentState)

# defining node name
node_name = "compliment"

# Adding nodes to the graph
graph.add_node(node_name, compliment_node)

# Add entry and exit point
graph.set_entry_point(node_name)
graph.set_finish_point(node_name)

# Compiling the graph
app = graph.compile()

# Invoking the app
result = app.invoke({"message": "Random"})

# Printing the result
print(result)