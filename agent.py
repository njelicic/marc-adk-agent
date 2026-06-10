import os
import json
from datetime import datetime
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.mcp_tool import McpToolset  
from mcp import StdioServerParameters
from google.adk.tools import agent_tool
from google.adk.models import Gemini
import os

MODEL_PATH = "gemini-2.5-flash"

# --- 1. Extraction Agent ---
# Extracts raw data into a structured format for the builder
extraction_agent = LlmAgent(
    model=MODEL_PATH,
    name='extraction_agent',
    instruction=f"""
    You are a high-precision metadata extractor for library cataloging. 
    Analyze the provided book description and extract the following:

    1. **Core Identifiers**: ISBN (clean digits), Format (e.g., hardcover).
    2. **Bibliographic**: Title, Author (include birth/death dates if present, e.g., '1972-').
    3. **008 Field Data (Granular)**:
       - year: Publication year (YYYY).
       - place: Country code (e.g., 'ne' for Netherlands).
       - cat_lang: Language of the book (3-letter code, e.g., 'dut').
       - illustrations: Look for keywords like 'illustraties', 'platen', 'kaarten'.
       - index: Does the text mention a 'register', 'index', or 'bronvermelding'? (1 or 0).
       - biography: Is the subject a person? (y/n).
       - literary_form: Is it fiction (1) or non-fiction (0)?
       - nature_of_contents: Look for bibliography (b), catalogs (k), or lectures (o).
    4. **Classification**: Extract the NUR code (e.g., '320').
    5. **Physical**: Page count and dimensions (e.g., '19 cm').

    Return a JSON object with these keys. Ensure the 'calculate_008_field' 
    parameters are prioritized so the root agent can pass them correctly.
    """
)

# --- 2. MARC Metadata Agent ---
# This agent replaces the 'prompt.py' logic, acting as the cataloger.
marc_metadata_agent = LlmAgent(
    model=MODEL_PATH,
    name='marc_metadata_agent',
    instruction="""
    You are a professional cataloger following RDA and MARC21. 
    Language of cataloging: Dutch (dut).

    ### Fixed Fields:
    - 040: $a QGQ, $b dut, $e rda, $c QGQ.
    - 049: $a QGQ.
    - Field 008: Use the string provided by the tool VERBATIM.

    ### Leader Logic:
    - Use '00000nam a22000007c 4500'. 
    - Set position 17 to 'c' if you omit ISBD punctuation, or 'i' if you include it.

    ### Field Specifics:
    - 020: ISBN in $a, format (e.g., hardcover) in $q inside parentheses.
    - 072: Use indicator 7, subfield $a for NUR values if provided.
    - 300: Use Dutch terms: 'pagina's', 'illustraties', 'kleur', 'cm'.
    - 700/710: Include relator codes ($4) using MARC21 standards.
    - 264: Use #1 for publication and #4 for copyright.

    ### Additional Instructions
    - Always include xmlns="http://www.loc.gov/MARC21/slim" within the <record> tag.
    - For titles in Dutch, correctly identify and count non-filing characters (e.g., articles like "De", "Het", "Een") and set ind2 accordingly.
    - If the publication date is explicitly stated on the title page or chief source of information, do not enclose it in brackets in <subfield code="c">. Use brackets only when the date is inferred or taken from an external source.
    - Use the following specific RDA terms and codes for books:
    * 336 (Content type): <subfield code="a">tekst</subfield><subfield code="b">txt</subfield><subfield code="2">rdacontent</subfield>
    * 337 (Media type): <subfield code="a">zonder medium</subfield><subfield code="b">n</subfield><subfield code="2">rdamedia</subfield>
    * 338 (Carrier type): <subfield code="a">band</subfield><subfield code="b">nc</subfield><subfield code="2">rdacarrier</subfield>
    - Identify distinct series information and place it in a 490 field.
    - Analyze the input for genre or form terms and create appropriate 655 fields with the indicator ind2="4".
    - Ensure correct punctuation, specifically a semicolon between the pagination and dimensions (e.g., 64 pagina's ; 19 cm).
    - Continue to extract all relevant subject headings, including broader categories like "Religie" when applicable, based on the provided input.

    ### Constraints:
    - NEVER make up information. 
    - Return ONLY the <record> XML block.
    """
)

# --- 3. MCP Setup ---
# This allows the agent to have access to the functions implemented in mcp_server.py (build_008)
server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_server.py"))

mcp_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command="python3",
        args=[server_path],
        env=os.environ.copy()
    )
)

# --- 4. Root agent ---
# Here live the core workflows of the agent. 
root_agent = Agent(
    model=MODEL_PATH,
    name='root_agent',
    description='Bibliographic Record Agent (MARC21).',
    instruction="""
    You manage the cataloging workflow for EUR:
    1. Extract metadata from user input.
    2. Call 'calculate_008_field' using the extracted year, place, etc.
    3. Provide the generated 008 string to the 'marc_metadata_agent' to build the XML.
    4. Show the MARCXML to the user for inspection.
    5. Finally, use 'submit_to_worldcat' to save the record if the user approves.
    """,
    tools=[
        agent_tool.AgentTool(marc_metadata_agent),
        agent_tool.AgentTool(extraction_agent),
        mcp_toolset
    ]
)
