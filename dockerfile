FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py MCPClient.py settings.py ./

COPY videos ./videos

ENV PYTHONUNBUFFERED=1 \
    MCP_SERVER_URL=http://host.docker.internal:3000 \
    UPLOAD_SERVER_URL=http://host.docker.internal:8080

CMD ["python", "agent.py"]