from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv
from os import getenv
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# loading the env variables
load_dotenv()

# Defining the global document content
document_content = ""

# Defining the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Defining tools to be used by the agent

# tool used to update the document content
@tool
def update(content: str) -> str:
    """Updates the document with the provided content"""

    global document_content
    document_content = content
    return f"Document has been updated successfully! The current content is:\n{document_content}"

# tool used to save the doc content into a file
@tool
def save(filename: str) -> str:
    """Save the current document to a text file and finish the process
    
    Args:
        filename: Name of the text file
    """

    global document_content
    
    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"
    
    try:
        with open(filename, 'w') as file:
            file.write(document_content)
        print(f"\nDocument has been saved to: {filename}")
        return f"Document has been saved successfully to {filename}"

    except Exception as e:
        return f"Error saving document: {e}"


# Defining the agent
def agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
        You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
    
        - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
        - If the user wants to save and finish, you need to use the 'save' tool.
        - Make sure to always show the current document state after modifications.
    
        The current document content is:{document_content}
    """)

    if not state['messages']:
        # user_input = "I'm ready to help you update a document. What would like to create?"
        # user_message = HumanMessage(content=user_input)
        message = AIMessage(content=f"I'm ready to help you update a document. What would like to create?")
    else:
        user_input = input("\nWhat would you like to do with the document?")
        print(f"\nUSER: {user_input}")
        message = HumanMessage(content=user_input)
    
    all_messages = [system_prompt] + list(state['messages']) + [message]


    response = llm.invoke(all_messages)

    print(f"\nAI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"\nUSING TOOLS: {[tc['name'] for tc in response.tool_calls ]}")
    
    return {"messages": list(state['messages']) + [message, response]}

# decision node
def should_continue(state: AgentState):
    """Determine if we should continue or end the conversations"""

    messages = state['messages']

    if not messages:
        return "continue"

    # Looking for the most recent tool message call
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage) and "saved" in msg.content.lower() and "document" in msg.content.lower():
            return "end"
    
    return "continue"


def print_messages(messages):
    """Function I made to print the messages in a more readable format"""
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\nTOOL RESULT: {message.content}")
 

# Defining list of tools
tools = [update, save]

# Defining the llm
llm = ChatOllama(model="qwen3:8b", base_url=getenv('OLLAMA_URL'), temperature=0).bind_tools(tools=tools)

# Creating the graph
graph = StateGraph(AgentState)

# Adding nodes
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))

# adding edges
graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges(
    "tools",
    should_continue, 
    {
        "continue": "agent",
        "end": END
    }
)


app = graph.compile()

def run():
    print("\n ====== DRAFTER ======")

    state = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])

if __name__ == "__main__":
    run()