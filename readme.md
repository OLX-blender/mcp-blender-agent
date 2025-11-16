### 1. Build the image
```bash
docker build -t mcp-blender-agent .
```

### 2. Run (can use .env file)
```bash
docker run -it --rm --env-file .env mcp-blender-agent
```

## Required variables (has backup in code - not required to set)

```bash
OPENAI_API_KEY=sk-...           # Your API key
MCP_SERVER_URL=http://...       # MCP server address (default localhost:3000)
UPLOAD_SERVER_URL=http://...    # Upload server address (default localhost:8080)
```

## Usage example

```
You: create a new session
You: list available tools
You: create python project for session <id> with 30 fps
```

## Stop
```bash
docker stop mcp-agent
```