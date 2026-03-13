from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from random import randint

# State schema
class AgentState(TypedDict):
    user: str
    guesses: List[int]
    lower: int
    upper: int

    correct: int
    hint: str
    guess: int
    counter: int

# Nodes
def setup_node(state: AgentState) -> AgentState:
    """Setups up the correct number to guesss"""

    state['correct'] = randint(state['lower'], state['upper'])
    state['counter'] = 0
    state['hint'] = ''
    return state

def guess_node(state: AgentState) -> AgentState:
    """Node that tries to guess the correct number"""

    if state['hint'] == 'higher':
        state['lower'] = state['guess'] + 1
        # lower = state['guess'] + 1
    elif state['hint'] == 'lower':
        state['upper'] = state['guess'] - 1
    
    state['counter'] += 1
    state['guess'] = (state['lower'] + state['upper']) // 2

    return state

def hint_node(state: AgentState) -> AgentState:
    """Tells if the guess is correct or not"""

    if state['guess'] < state['correct']:
        state['hint'] = 'higher'
    else:
        state['hint'] = 'lower'

    state['guesses'].append(state['guess'])

    return state

def decision_node(state: AgentState) -> AgentState:
    if state['counter'] == 7:
        print("FAILED to guess the number, guesses:", state['guesses'])
        return 'exit'
    elif state['guess'] == state['correct']:
        print("Guessed the correct number: ", state['correct'])
        return 'exit'

    return 'continue'

# Graph
graph = StateGraph(AgentState)

# adding node
graph.add_node("setup_node", setup_node)
graph.add_node("guess_node", guess_node)
graph.add_node("hint_node", hint_node) # pass throguh since we are not returnig the state

# adding edges
graph.add_edge(START, "setup_node")
graph.add_edge("setup_node", "guess_node")
graph.add_edge("guess_node", "hint_node")
graph.add_conditional_edges("hint_node", decision_node, {
    "continue": "guess_node",
    "exit": END # ending the loop
})

# compiling the graph
app = graph.compile()

result = app.invoke({'user': 'Random', 'lower': 1, 'upper': 20, 'guesses': [], 'counter': -1})
print(result)