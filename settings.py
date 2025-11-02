import os
from dotenv import load_dotenv

load_dotenv()

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
MCP_ENDPOINT = "/mcp"

# Upload Server Configuration
UPLOAD_SERVER_URL = os.getenv("UPLOAD_SERVER_URL", "http://localhost:8080")
UPLOAD_ENDPOINT = "/upload"

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-chat"
MODEL_TEMPERATURE = 0

# MCP Protocol
MCP_PROTOCOL_VERSION = "2024-11-05"
