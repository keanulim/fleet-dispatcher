import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools import query_available_trucks, get_active_missions, check_route_conditions, query_safety_regulations, dispatch_truck

# 1. Initialize the Model
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

# 2. Define the tools list
tools = [query_available_trucks, get_active_missions, check_route_conditions, query_safety_regulations, dispatch_truck]

# 3. Use the PREBUILT agent (this handles the "ValueError" internally)
bot_os = create_react_agent(llm, tools) # type: ignore