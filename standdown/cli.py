# standdown/cli.py

import uvicorn
from standdown import server

def start_server(port: int):
    print(f"[SERVER] Starting standdown FastAPI server on port {port}")
    uvicorn.run(server.app, host="0.0.0.0", port=port)
