from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.types import interrupt
from langgraph.prebuilt import ToolNode,tools_condition


load_dotenv()
@tool()
def human_assistance_tool(query: str):
    """Request assistance from a human."""
    human_response = interrupt({"query": query}) # Grpah will exit out after saving data in the DB
    return human_response["data"] # resume with the data


tools = [human_assistance_tool]
llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools = tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    # messages = state.get("messages")
    # response = llm.invoke(messages)
    # return { "messages": [response]}
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}

tool_node = ToolNode(tools = tools)
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
# graph.interrupt_after_nodes("confirm_transaction")


def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer = checkpointer)


