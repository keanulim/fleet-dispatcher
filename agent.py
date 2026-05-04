from langgraph.graph import StateGraph, END
from state import AgentState, MissionDecision
from tools import fetch_weather, fetch_truck_status


# --- NODES: The steps in the reasoning process ---

def observer_node(state: AgentState):
    """Step 1: Gather real-time data."""
    dest = state["shipment_request"].get("destination", "Dallas")
    truck_id = state["shipment_request"].get("truck_id", "BOT-001")

    return {
        "weather_data": fetch_weather(dest),
        "truck_telemetry": fetch_truck_status(truck_id)
    }


def auditor_node(state: AgentState):
    """Step 2: Cross-reference data with Safety Laws (RAG)."""
    # Simulate a RAG lookup here
    reg_text = "TX Law: Humanless flight prohibited if visibility < 0.25 miles."
    return {"regulatory_check": reg_text}


def decider_node(state: AgentState):
    """Step 3: The LLM processes everything and decides."""
    # Logic: Compare weather visibility vs regulation text
    viz = state["weather_data"]["visibility_miles"]

    if viz < 0.25:
        decision = MissionDecision(
            is_authorized=False,
            risk_level="High",
            reasoning=f"Visibility {viz} is below the legal threshold of 0.25mi.",
            warnings=["Weather Violation"]
        )
    else:
        decision = MissionDecision(
            is_authorized=True,
            risk_level="Low",
            reasoning="All systems optimal and weather within ODD limits.",
            warnings=[]
        )
    return {"mission_output": decision}


# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)
workflow.add_node("observe", observer_node)
workflow.add_node("audit", auditor_node)
workflow.add_node("decide", decider_node)

workflow.set_entry_point("observe")
workflow.add_edge("observe", "audit")
workflow.add_edge("audit", "decide")
workflow.add_edge("decide", END)

orchestrator = workflow.compile()