# MARC Agent

A bibliographic record cataloging agent built with [Google ADK](https://google.github.io/adk-docs/). It uses a multi-agent pipeline (extraction → 008 field calculation → MARC21 XML generation) and exposes tools via an MCP server.

## Prerequisites

- Python 3.10+
- A Google API key with access to Gemini models

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (never commit this file):

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

## Running the agent

Start the ADK web interface:

```bash
adk web
```

Then open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Architecture

| Component | File | Role |
|---|---|---|
| Root agent | `agent.py` | Orchestrates the full cataloging workflow |
| Extraction agent | `agent.py` | Extracts structured metadata from raw book descriptions |
| MARC metadata agent | `agent.py` | Builds MARC21 XML following RDA rules |
| MCP server | `mcp_server.py` | Exposes `calculate_008_field` and `submit_to_worldcat` as tools |
| 008 field builder | `handlers/field_008.py` | Constructs the 40-character MARC 008 fixed field |
| OCLC API handler | `handlers/oclc_api.py` | Submits records to WorldCat |
