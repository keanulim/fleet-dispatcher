import asyncio
from agent import orchestrator

async def run_dispatch_test():
    # 1. Mock a real request from Ryan Transportation (Bot Auto's Partner)
    # Route: Houston (Riggy's) to Hutchins (Safe Stop)
    shipment_request = {
        "truck_id": "BOT-012",
        "cargo": "Server Racks",
        "origin": "Houston",
        "destination": "Hutchins",
        "departure_time": "2026-05-04T03:00:00"
    }

    print(f"--- INITIALIZING DISPATCH FOR: {shipment_request['cargo']} ---")

    # 2. Initialize the State
    initial_state = {
        "shipment_request": shipment_request,
        "weather_data": None,
        "truck_telemetry": None,
        "regulatory_check": None,
        "mission_output": None,
        "error": None
    }

    final_state = initial_state
    async for output in orchestrator.astream(initial_state):
        for node, data in output.items():
            if data is None: continue

            # Update our tracker so we have the full state at the end
            final_state.update(data)

            print(f"\n[NODE COMPLETED]: {node}")

            # Print intermediate updates
            if 'weather_data' in data:
                w = data['weather_data']
                print(f"   -> Weather: {w.get('condition')}, {w.get('visibility_miles')}mi visibility")

            if 'regulatory_check' in data:
                print(f"   -> Safety Law: {data['regulatory_check']}")

    # 4. FINAL RECAP (Outside the loop to ensure it prints)
    print("\n" + "=" * 40)
    print("FINAL MISSION CONTROL REPORT")
    print("=" * 40)

    decision = final_state.get('mission_output')
    if decision:
        status = "✅ AUTHORIZED" if decision.decision == "AUTHORIZED" else "❌ REJECTED"
        print(f"STATUS: {status}")
        print(f"REASONING: {decision.reasoning}")
        print(f"RISK LEVEL: {decision.risk_level}")
    else:
        print("⚠️ Error: No decision was reached by the orchestrator.")

if __name__ == "__main__":
    asyncio.run(run_dispatch_test())