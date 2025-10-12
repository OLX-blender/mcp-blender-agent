import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()


@tool
def upload_video(file_path: str, session_id: str) -> str:
    """Upload video file to server. Args: file_path, session_id"""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"

        url = f"{os.getenv('UPLOAD_SERVER_URL', 'http://localhost:8080')}/upload?sessionId={session_id}"
        with open(file_path, "rb") as f:
            response = requests.post(
                url, files={"file": (path.name, f, "application/octet-stream")}
            )

        return response.json() if response.ok else f"Error: {response.json()}"
    except Exception as e:
        return f"Error: {e}"


llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

agent = create_tool_calling_agent(
    llm,
    [upload_video],
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You can upload video files. Use upload_video tool with file_path and session_id.",
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ),
)

executor = AgentExecutor(agent=agent, tools=[upload_video], verbose=True)

if __name__ == "__main__":
    result = executor.invoke({"input": input("Command: ")})
    print(result["output"])
