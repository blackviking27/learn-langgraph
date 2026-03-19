from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from os import getenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# load env
load_dotenv()

# Agent State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Defining tools
@tool
def add(a: int, b: int):
    """This tool will be used to add 2 numbers"""
    return a + b

@tool
def substract(a: int,b: int):
    """This tool will be used to substract 2 numbers"""
    return a - b

@tool
def multiply(a: int, b: int):
    """This tool will used to multiply 2 numbers"""
    return a * b

# Adding tools
tools = [add, substract, multiply]

# Defining model
llm = ChatOllama(model="qwen3:8b", base_url=getenv('OLLAMA_URL'), temperature=0).bind_tools(tools=tools)

# Defining nodes
def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="You are my AI assistant, please answer my query to the best of your ability.")

    response = llm.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}

# decision node
def should_continue(state: AgentState):
    messages =state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


# graph
graph = StateGraph(AgentState)

# adding nodes
graph.add_node("agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)


# adding edges
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "continue": "tools",
    "end": END
})
graph.add_edge("tools", "agent")


app = graph.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# inputs = {"messages": [("user", "Add 40 + 12 and then multiply the result by 6. Also tell me a joke please.")]}
inputs = {"messages": [("user", "Add 40 + 12 and then substract 47 from it")]}
print_stream(app.stream(inputs, stream_mode="values"))
