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
        args = json.loads(arguments) if arguments else {}
        result = mcp_client.call_tool(tool_name, args)

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

# Get dynamic MCP tools list for system prompt
mcp_tools_list = mcp_client.list_tools()
if mcp_tools_list:
    tools_description = "\n".join(
        [f"- {t['name']}: {t['description']}" for t in mcp_tools_list]
    )
else:
    tools_description = "No MCP tools available (server offline)"

system_prompt = f"""You are a Blender video editing assistant. You can:
1. Upload video files using upload_video tool
2. List available MCP tools using list_mcp_tools
3. Execute MCP tools using call_mcp_tool

Available MCP tools:
{tools_description}

Always provide arguments as a valid JSON string for MCP tools."""

agent = create_tool_calling_agent(
    llm,
    tools,
    ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ),
)

executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    print(f"MCP Server: {MCP_SERVER_URL}")
    print(f"Upload Server: {UPLOAD_SERVER_URL}")
    print(f"Model: {MODEL_NAME}")

    print("\nConnecting to MCP server...")
    startup_tools = mcp_client.list_tools()
    if startup_tools:
        print(f"Connected! Found {len(startup_tools)} tools")
        print("\nAvailable MCP tools:")
        for mcp_tool in startup_tools:
            print(f" {mcp_tool['name']}: {mcp_tool['description']}")
    else:
        print("MCP server not available")

    print("\nType 'exit' or 'quit' to stop")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            result = executor.invoke({"input": user_input})
            print(f"\nAgent: {result['output']}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
