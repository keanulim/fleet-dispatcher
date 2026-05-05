from typing import Annotated, TypedDict, Union, List
from pydantic import BaseModel, Field

# 1. The Structured Output we want from the LLM
class MissionDecision(BaseModel):
    decision: str = Field(description="AUTHORIZED, REJECTED, or PENDING_HUMAN")
    risk_level: str = Field(description="Low, Medium, or High risk assessment") # <--- Add this!
    reasoning: str = Field(description="Explanation of safety logic")
    constraints: List[str] = Field(description="List of safety ODDs checked")

# 2. The Shared State
class AgentState(TypedDict):
    shipment_request: dict
    weather_data: dict
    truck_telemetry: dict
    regulatory_check: str
    mission_output: MissionDecision