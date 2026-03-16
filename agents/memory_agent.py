from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph
from dotenv import load_dotenv

load_dotenv()

# state
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

# llm
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=1.0, max_tokens=None, timeout=None, max_retries=2)

# node
def process(state: AgentState) -> AgentState:
    """This node is invoked to solve the user problem"""
    response = llm.invoke(state["messages"])

    state["messages"].append(AIMessage(content=response.content))
    print("\AI:", response.content)
    return state

# Graph
graph = StateGraph(AgentState)

# add nodes
graph.add_node("process", process)

# add edge
graph.add_edge(START, "process")
graph.add_edge("process", END)

# app
app = graph.compile()

# Creating a conversation history outside of graph state
conversation_history = []

# taking user input
user_input = input("Enter: ")
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    response = app.invoke({"messages": conversation_history})

    conversation_history = response["messages"]
    user_input = input("Enter: ")


# file path
path = "logging.txt"

# Dumping the conversation into a file
with open(path, "w") as file:
    file.write("Your conversation log:\n\n\n")

    for msg in conversation_history:
        if isinstance(msg, HumanMessage):
            file.write(f"You:{msg.content}\n")
        elif isinstance(msg, AIMessage):
            file.write(f"AI:{msg.content}\n")
    
    file.write(f"End of conversation")

print(f"\n\nConversation saved to file: {path}")