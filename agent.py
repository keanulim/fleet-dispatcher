import json
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from tools import query_available_trucks, get_active_missions, check_route_conditions, query_safety_regulations

# --- 1. SETUP THE TOOLS ---
# We map the tools so the LLM knows what functions are available
tools = {
    "query_available_trucks": query_available_trucks,
    "get_active_missions": get_active_missions,
    "check_route_conditions": check_route_conditions,
    "query_safety_regulations": query_safety_regulations
}

# Define the tool definitions for the LLM
tool_definitions = [
    {
        "name": "query_available_trucks",
        "description": "Returns a list of healthy, idle trucks ready for new jobs.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_active_missions",
        "description": "Returns details on all trucks currently on deliveries.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "check_route_conditions",
        "description": "Checks weather for a specific location (e.g. 'Madisonville').",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"]
        }
    },
    {
        "name": "query_safety_regulations",
        "description": "Searches for autonomous vehicle safety laws and FMCSA rules.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
]


# --- 2. DEFINE THE STATE ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The conversation history"]


# --- 3. THE NODES ---

model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tool_definitions)


def call_model(state: AgentState):
    """The LLM decides what to do next."""
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def call_tool(state: AgentState):
    """Executes the tool the LLM requested."""
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        # Execute the actual Python function from tools.py
        result = tools[tool_name](**tool_args)

        tool_messages.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=json.dumps(result)
        ))

    return {"messages": tool_messages}


# --- 4. THE GRAPH ---

workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

workflow.set_entry_point("agent")


# Logic: If the model called a tool, go to 'action'. Otherwise, finish.
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "continue"
    return "end"


workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)

workflow.add_edge("action", "agent")

bot_os = workflow.compile()