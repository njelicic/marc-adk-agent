import os
from mcp.server.fastmcp import FastMCP
import uuid

from handlers.field_008 import build_008
from handlers.oclc_api import get_access_token, create_bib_record

# Initialize the MCP Server
mcp = FastMCP("MARC21 Cataloging Server")

@mcp.tool()
@mcp.tool()
def calculate_008_field(
    year: str,
    place: str = "ne",
    index: str = "0",
    biography: str = " ",
    cat_lang: str = "dut",
    type_of_date: str = "s",
    illustrations: list = None,
    target_audience: str = " ",
    form_of_item: str = " ",
    nature_of_contents: list = None,
    government_pub: str = " ",
    conference_pub: str = "0",
    festschrift: str = "0",
    literary_form: str = "0"
) -> str:
    """
    Constructs a 40-character MARC 008 string. 
    The agent should analyze the book description to determine these values.
    Build a valid 40-character MARC21 008 field for books (LDR/06=a, 07=m).
    All inputs are validated and padded to the correct positional lengths.

    Position map:
      00-05  Date entered on file (auto: today YYMMDD)
      06     Type of date
      07-10  Date 1
      11-14  Date 2
      15-17  Place of publication
      18-21  Illustrations (up to 4 codes, space-padded)
      22     Target audience
      23     Form of item
      24-27  Nature of contents (up to 4 codes, space-padded)
      28     Government publication
      29     Conference publication
      30     Festschrift
      31     Index
      32     Undefined (always blank)
      33     Literary form
      34     Biography
      35-37  Language
      38     Modified record
      39     Cataloging source
    """
    return build_008(
        date1=year,
        place=place,
        index=index,
        biography=biography,
        language=cat_lang,
        type_of_date=type_of_date,
        illustrations=illustrations or [],
        target_audience=target_audience,
        form_of_item=form_of_item,
        nature_of_contents=nature_of_contents or [],
        government_pub=government_pub,
        conference_pub=conference_pub,
        festschrift=festschrift,
        literary_form=literary_form
    )

@mcp.tool()
def submit_to_worldcat(marcxml: str) -> None:
    """
    Submits a generated MARCXML record to OCLC WorldCat via the Metadata API.
    """
    with open(f'{uuid.uuid4()}.txt','w') as f:
        f.write(marcxml)
        return

# @mcp.tool()
# def submit_to_worldcat(marcxml: str) -> str:
#     """
#     Submits a generated MARCXML record to OCLC WorldCat via the Metadata API.
#     """
#     try:
#         # Load credentials using existing config handler
#         creds = load_credentials()
#         token, _ = get_access_token(creds["client_id"], creds["client_secret"])

#         # Execute the creation logic from oclc_api.py
#         response_text, status_code, _ = create_bib_record(marcxml, token)

#         if status_code in (200, 201):
#             return f"Success! Record created. OCLC Response: {response_text[:200]}"
#         else:
#             return f"Error {status_code}: {response_text[:500]}"
            
#     except Exception as e:
#         return f"Failed to submit record: {str(e)}"

if __name__ == "__main__":
    mcp.run()