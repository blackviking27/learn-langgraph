from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# State schema
class AgentState(TypedDict):
    number1: int
    number2: int
    number3: int
    number4: int
    operation1: str
    operation2: str
    result1: int
    result2: int

# Defining node
def adder1(state: AgentState) -> AgentState:
    """This node adds 2 numbers"""
    state['result1'] = state['number1'] + state['number2']

    return state

def adder2(state: AgentState) -> AgentState:
    """This node adds 2 numbers"""
    state['result2'] = state['number3'] + state['number4']

    return state

def substractor1(state:AgentState) -> AgentState:
    """This node substract 2 numbers"""
    state['result1'] = state['number1'] - state['number2']

    return state

def substractor2(state:AgentState) -> AgentState:
    """This node substract 2 numbers"""
    state['result2'] = state['number3'] - state['number4']

    return state

def router1(state: AgentState) -> AgentState:
    """This node decides the path to take"""
    if state['operation1'] == '+':
        return "addition_op"
    elif state['operation1'] == '-':
        return "substraction_op"

def router2(state: AgentState) -> AgentState:
    """This node decides the path to take"""
    if state['operation2'] == '+':
        return "addition_op"
    elif state['operation2'] == '-':
        return "substraction_op"

# Creating graph
graph = StateGraph(AgentState)

# Adding node
graph.add_node('add_node1', adder1)
graph.add_node('add_node2', adder2)

graph.add_node('subtract_node1', substractor1)
graph.add_node('subtract_node2', substractor2)

graph.add_node('router_node1', lambda state: state) # Pass through function
graph.add_node('router_node2', lambda state: state) # Pass through function

# Adding edges
graph.add_edge(START, "router_node1")
graph.add_conditional_edges("router_node1", router1, {
    "addition_op": "add_node1",
    "substraction_op": "subtract_node1"
})

graph.add_edge("add_node1", "router_node2")
graph.add_edge("subtract_node1", "router_node2")

graph.add_conditional_edges("router_node2", router2, {
    "addition_op": "add_node2",
    "substraction_op": "subtract_node2"
})

graph.add_edge("add_node2", END)
graph.add_edge("subtract_node2", END)


# Compiling the graph
app = graph.compile()

result = app.invoke({
    'number1': 5,
    'number2': 5,
    'number3': 10,
    'number4': 10,
    'operation1': "+",
    'operation2': "+"
})

print(result)