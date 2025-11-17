### 1. Build the image
```bash
docker build -t mcp-blender-agent .
```

### 2. Run (can use .env file)
```bash
docker run -it --rm --env-file .env mcp-blender-agent
```

## Required variables

```bash
OPENAI_API_KEY=sk-...           # Your API key
MODEL_NAM=...
OPENAI_API_BASE=https://...
OPTIONAL MCP_SERVER_URL=http://...
OPTIONAL UPLOAD_SERVER_URL=http://...
```

## Usage example

```
Stwórz proszę nową sesję, zapamiętaj ją. Dla tej sesji prześlij filmik videos/test.mp4. Następnie w ramach tej samej sesji utwórz projekt python. Po utworzeniu projektu python dodaj do niego ścieżkę do filmiku test.mp4. Na koniec zrenderuj całość.
```

## Stop
```bash
docker stop mcp-agent
```