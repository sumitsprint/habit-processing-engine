
from dotenv import load_dotenv
import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools import agent_tool # new addition
from pydantic import BaseModel
from typing import Literal


load_dotenv()

MODEL = LiteLlm(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)


MCP_SERVER_SCRIPT = str(Path(__file__).parent / "mcp_server.py") 


habit_processing_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='python',
            args=[MCP_SERVER_SCRIPT],
        )
    )
)

# define a class
class HabitResolution(BaseModel):
    status: Literal["matched", "not_found", "ambiguous", "list_all"]
    habit_name: str | None = None
    habit_type: Literal["YES_NO", "NUMERICAL"] | None = None
    candidates: list[dict] | None = None
    message: str | None = None


habit_resolver_agent = LlmAgent(
    name="habit_resolver",
    model=MODEL,
    description="Identifies the database habit name matching the user's request, or returns all available habits along with their types.",
    instruction="""You are a Habit Name Resolution Agent. Your sole responsibility is to map a user's informal habit query to the exact habit name stored in the database, or list all available habits if requested.

### Workflow:
1. Call the `list_habits` tool to retrieve the list of habit dictionaries (each containing "name" and "type") from the database.
2. If the user asks to see or list all available habits, populate the output schema with all retrieved habit dictionaries.
3. Otherwise, compare the user's requested habit against the retrieved list using semantic and substring matching on the "name" field.
4. Determine the match status and populate the output schema according to the Decision Rules below.

### Decision Rules:
- **Status: "list_all"**
  - Trigger: The user asks to see, show, or list all habits (e.g., "what habits do I have?", "list all habits").
  - Set `status` = "list_all"
  - Set `habit_name` = null
  - Set `habit_type` = null
  - Set `candidates` = The complete list of habit dictionaries returned by `list_habits`.
  - Set `message` = null

- **Status: "matched"**
  - Trigger: Exactly ONE habit dictionary clearly matches the user's intent.
  - Set `status` = "matched"
  - Set `habit_name` = The exact "name" string from the matched dictionary.
  - Set `habit_type` = The exact "type" string from the matched dictionary ("YES_NO" or "NUMERICAL").
  - Set `candidates` = null
  - Set `message` = null

- **Status: "ambiguous"**
  - Trigger: Multiple habit dictionaries in the database could reasonably match the user's request.
  - Set `status` = "ambiguous"
  - Set `habit_name` = null
  - Set `habit_type` = null
  - Set `candidates` = List of all potentially matching habit dictionaries.
  - Set `message` = null

- **Status: "not_found"**
  - Trigger: No habit in the database matches the user's query even loosely.
  - Set `status` = "not_found"
  - Set `habit_name` = null
  - Set `habit_type` = null
  - Set `candidates` = null
  - Set `message` = "No such habit found in the database."

### Constraints:
- Never invent, modify, or correct the casing/spelling of the habit name. Use the exact "name" string returned by `list_habits`.
- Do not perform any habit analysis or calculations yourself; your only job is name and type resolution.""",
    tools=[habit_processing_tools],
    output_schema=HabitResolution,
    output_key="habit_resolution_json",
)

# agent tool

resolver_tool = agent_tool.AgentTool(agent=habit_resolver_agent) # Agenttool takes the agent's internal name,
# AgentTool is a Single Tool: It wraps exactly one agent and turns it into one callable function.

root_agent = LlmAgent(
    name="habit_analysis",
    model=MODEL,
    instruction="""
You are a Habit Analysis Assistant. Your role is to help users view and analyze their habit data using your available tools.

### Workflow:
1. Whenever a user asks about a habit or requests to list all habits:
   - If they ask about a specific habit, extract the informal habit name from their message.
   - If they ask to see all habits, treat it as a full habit list request.
   - Call `habit_resolver` to resolve the extracted name to the exact database name, or to retrieve the complete habit list.

2. Inspect the result returned by `habit_resolver` and take one of the following actions based on `status`:
   - If `status` is "matched": Pass the exact `habit_name` to the `analyze_habit` tool.
   - If `status` is "ambiguous": Present the list of `candidates` to the user and ask them to clarify which habit they meant. Do NOT call `analyze_habit`.
   - If `status` is "not_found": Reply to the user with the `message` provided by the resolver. Do NOT call `analyze_habit`.
   - If `status` is "list_all": Present the full list of habits from `candidates` to the user in a bulleted list.

3. When `analyze_habit` returns results, summarize the findings clearly for the user.

### Constraints:
- Never guess or modify a habit name; only use the exact `habit_name` provided by `habit_resolver`.
- Do not invent metrics or make claims unsupported by the returned results from `analyze_habit`.
""",
    tools=[habit_processing_tools, resolver_tool], # adk unpacks everything into a flat list of individual functions
) 


