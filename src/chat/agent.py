import requests
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from pyalex import Works
from typing import List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.parser import parse_nul_search, parse_digital_collections, parse_open_alex

PRIMO_URL = "https://search.library.northwestern.edu/primaws/rest/pub/pnxs"
DC_URL = "https://api.dc.library.northwestern.edu/api/v2/search"
SYSTEM_PROMPT = """
You are a research assistant with access to Northwestern University Library's search interface. Your role is to guide people to useful collections materials. Tools you can access include NUL search for general collections, Digital Collections for digitized and special collections, and OpenAlex for open citations on the web.

Present your responses in Markdown format with:
- Full citations using proper markdown links: [Title](permalink)
- Digital Collections items linked as: [Title](https://dc.library.northwestern.edu/items/item-id)
- Key findings in bulleted lists
- Section headers using appropriate markdown levels
- Additional suggestions for further research in a separate section

Example format:
## Research Summary
[Brief overview of findings]

### Key Sources
- [Title of Source](permalink) - Description

### Key Findings
- Finding 1
- Finding 2

### Further Research Suggestions
- Suggestion 1
- Suggestion 2

### MLA Citations
- Properly formatted citations
"""

class Agent:
    def __init__(self, callbacks: Optional[List[BaseCallbackHandler]] = None):
        self.callbacks = callbacks or []
        self.tools = self._create_tools()
        self.model = self._create_model()
        self.checkpointer = MemorySaver()
        self.app = create_react_agent(self.model, self.tools, checkpointer=self.checkpointer)

    def _create_tools(self):
        @tool(response_format="content_and_artifact")
        def nul_search(query: str):
            """Search the NUL database for a given query. Returns a list of results."""
            session = requests.Session()
            params = {
                "q": f"any,contains,{query}",
                "vid": "01NWU_INST:NULVNEW",
                "scope": "MyInst_and_CI",
                "lang": "en",
                "offset": "0",
                "limit": "5",
                "sort": "rank",
                "pcAvailability": "true",
            }
            response = session.get(PRIMO_URL, params=params)
            parsed = parse_nul_search(response.json())
            return parsed, None

        @tool(response_format="content_and_artifact")
        def open_alex(query: str):
            """Search OpenAlex for a given query. Returns a list of citations."""
            citations = Works().search(query).select(["id", "title", "publication_year", "language", "authorships"]).get(per_page=5)
            parsed = parse_open_alex(citations)
            return parsed, None
        
        @tool(response_format="content_and_artifact")
        def digital_collections(query: str):
            """Search for unique and special digitized resources from Northwestern University Library's Digital Collections for a given query. Returns a list of results."""
            session = requests.Session()
            params = {"query": query, "size": "5", "as": "iiif"}
            response = session.get(DC_URL, params=params)
            parsed = parse_digital_collections(response.json())
            return parsed, None

        return [nul_search, open_alex, digital_collections]

    def _create_model(self):
        return ChatBedrock(
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            temperature=0,
            callbacks=self.callbacks,
            system_prompt_with_tools=SYSTEM_PROMPT,
            streaming=True,
        )

    def invoke(self, input_data: dict, config: Optional[dict] = None):
        """Invoke the agent with the given input and configuration."""
        return self.app.invoke(input_data, config=config)