"""Start the ADK web UI without the adk.exe CLI (bypasses group policy block).
Usage: python start_web.py [--host 127.0.0.1] [--port 8000]
"""
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()

# The agents_dir must be the parent of the agent package folder(s).
agents_dir = str(Path(__file__).parent)

from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(
    agents_dir=agents_dir,
    web=True,
    host=args.host,
    port=args.port,
)

import uvicorn

uvicorn.run(app, host=args.host, port=args.port)
