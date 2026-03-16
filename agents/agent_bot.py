from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

# importing the env val
load_dotenv()

# Agent state
class AgentState(TypedDict):
    messages: List[HumanMessage]


# Initializing llm
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=1.0, max_tokens=None, timeout=None, max_retries=2)

# Process Node
def process(state: AgentState) -> AgentState:
    response = llm.invoke(state['messages'])
    print(f"AI: {response.content}")
    return state

graph = StateGraph(AgentState)

# Adding node
graph.add_node("process", process)

# edges
graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()

user_input = input("Enter:")
while user_input != "exit":
    agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter:")

