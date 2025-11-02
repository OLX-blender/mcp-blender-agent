import json
from pathlib import Path

import requests
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from MCPClient import MCPClient
from settings import (
    MCP_SERVER_URL,
    MODEL_NAME,
    MODEL_TEMPERATURE,
    OPENAI_API_BASE,
    OPENAI_API_KEY,
    UPLOAD_SERVER_URL,
)

# Initialize MCP client
mcp_client = MCPClient(MCP_SERVER_URL)


@tool
def upload_video(file_path: str, session_id: str) -> str:
    """Upload video file to server. Args: file_path, session_id"""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"

        url = f"{UPLOAD_SERVER_URL}/upload?sessionId={session_id}"
        with open(file_path, "rb") as f:
            response = requests.post(
                url, files={"file": (path.name, f, "application/octet-stream")}
            )

        return response.json() if response.ok else f"Error: {response.json()}"
    except Exception as e:
        return f"Error: {e}"


@tool
def list_mcp_tools() -> str:
    """List all available MCP tools"""
    try:
        tools = mcp_client.list_tools()
        if not tools:
            return "No MCP tools available"

        result = ["Available MCP Tools:\n"]
        for t in tools:
            result.append(f"• {t['name']}: {t['description']}")

        return "\n".join(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def call_mcp_tool(tool_name: str, arguments: str = "{}") -> str:
    """
    Call an MCP tool with the given arguments.

    Args:
        tool_name: Name of the MCP tool to call
        arguments: JSON string with tool arguments (e.g., '{"param": "value"}')

    Returns:
        Result from the MCP tool
    """
    try:
        # Parse arguments
        args = json.loads(arguments) if arguments else {}

        # Call the tool
        result = mcp_client.call_tool(tool_name, args)

        # Extract text from content array (MCP standard response format)
        if isinstance(result, dict) and "content" in result:
            texts = [
                c.get("text", "") for c in result["content"] if c.get("type") == "text"
            ]
            return "\n".join(texts) if texts else str(result)

        return str(result)
    except json.JSONDecodeError as e:
        return f"Invalid JSON arguments: {e}"
    except Exception as e:
        return f"Error calling MCP tool '{tool_name}': {e}"


# Initialize LLM
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=MODEL_TEMPERATURE,
    api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_API_BASE,
)

# Create agent with all tools
tools = [upload_video, list_mcp_tools, call_mcp_tool]

agent = create_tool_calling_agent(
    llm,
    tools,
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Blender video editing assistant. You can help users:
1. Upload video files using upload_video tool
2. List available MCP tools using list_mcp_tools
3. Execute MCP tools using call_mcp_tool

Workflow:
- Create session: call_mcp_tool("create_session", "{{}}")
- Upload video: upload_video("path/to/video.mp4", "session_id")
- Create project: call_mcp_tool("create_python_project", '{{"sessionId": "xxx", "fps": 30}}')
- Add videos: call_mcp_tool("add_video_filenames_to_script", '{{"sessionId": "xxx", "videoFilenames": ["video.mp4"]}}')
- Render: call_mcp_tool("run_blender_rendering_script", '{{"sessionId": "xxx"}}')

Always provide arguments as a JSON string for MCP tools.""",
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ),
)

executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    print("MCP Blender Agent")
    print(f"MCP Server: {MCP_SERVER_URL}")
    print(f"Upload Server: {UPLOAD_SERVER_URL}")

    # Connect to MCP server
    print("\nConnecting to MCP server...")
    startup_tools = mcp_client.list_tools()
    if startup_tools:
        print(f"Connected! Found {len(startup_tools)} tools")
    else:
        print("MCP server not available")

    print("\nType 'exit' or 'quit' to stop")

    # Main loop
    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n Goodbye!")
                break

            if not user_input:
                continue

            result = executor.invoke({"input": user_input})
            print(f"\nAgent: {result['output']}\n")

        except KeyboardInterrupt:
            print("\n\n Goodbye!")
            break
        except Exception as e:
            print(f"\n Error: {e}\n")
