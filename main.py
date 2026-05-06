import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from agent import bot_os
from langchain_core.messages import HumanMessage


async def main():
    print("\n--- BotOS Fleet Command & Control Initialized ---")

    # Persistent history for the session
    history = []

    while True:
        user_input = input("Fleet Manager > ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Run the agent
        # We pass the full history plus the new input
        inputs = {"messages": history + [HumanMessage(content=user_input)]}

        async for chunk in bot_os.astream(inputs, stream_mode="values"):
            final_msg = chunk["messages"][-1]

            # Extract and print the final response as normal text
        if final_msg.content:
            content = final_msg.content

            # Handle the Gemini-specific list format
            if isinstance(content, list):
                # Joins all text parts together into one string
                clean_text = " ".join([part['text'] for part in content if 'text' in part])
            else:
                clean_text = content

            print(f"\n[BotOS]: {clean_text}\n")

            # Update history for the next turn
            history = chunk["messages"]
            history = history[-10:]


if __name__ == "__main__":
    asyncio.run(main())