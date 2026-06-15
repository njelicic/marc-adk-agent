# MARC Agent

A bibliographic record cataloging agent built with [Google ADK](https://google.github.io/adk-docs/). It uses a multi-agent pipeline (extraction → 008 field calculation → MARC21 XML generation) and exposes tools via an MCP server.

## Project structure

```
marc_agent/                  ← repo root
├── .env                     ← secrets (never commit)
├── requirements.txt
├── start_web.py             ← recommended launcher (bypasses adk CLI)
└── marc_agent/              ← ADK agent package
    ├── __init__.py
    ├── agent.py             ← extraction, MARC metadata, and root agents
    ├── mcp_server.py        ← MCP server (calculate_008_field, submit_to_worldcat)
    └── handlers/
        ├── config.py        ← OCLC credentials + institution config
        ├── field_008.py     ← 008 fixed-field builder
        ├── oclc_api.py      ← WorldCat Metadata API client
        └── prompt.py        ← legacy prompt builder (fallback path)
```

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

### Recommended — `start_web.py`

Use this script when the `adk` CLI is unavailable (e.g. blocked by group policy):

```bash
python start_web.py
# optional flags:
python start_web.py --host 0.0.0.0 --port 8080
```

### Alternative — ADK CLI

```bash
adk web
```

Then open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Architecture

| Component | File | Role |
|---|---|---|
| Root agent | `marc_agent/agent.py` | Orchestrates the full cataloging workflow |
| Extraction agent | `marc_agent/agent.py` | Extracts structured metadata from raw book descriptions |
| MARC metadata agent | `marc_agent/agent.py` | Builds MARC21 XML following RDA rules |
| MCP server | `marc_agent/mcp_server.py` | Exposes `calculate_008_field` and `submit_to_worldcat` as MCP tools |
| 008 field builder | `marc_agent/handlers/field_008.py` | Constructs the 40-character MARC 008 fixed field |
| OCLC API client | `marc_agent/handlers/oclc_api.py` | WorldCat Metadata API (submit bib records) |
| Credential store | `marc_agent/handlers/config.py` | Encrypted OCLC credentials + institution config |
| Legacy prompt builder | `marc_agent/handlers/prompt.py` | Builds the AI cataloging prompt (fallback path) |

> **Note:** `submit_to_worldcat` currently writes the MARCXML to a local `.txt` file. The live WorldCat API call is implemented in `handlers/oclc_api.py` but commented out in `mcp_server.py`.
