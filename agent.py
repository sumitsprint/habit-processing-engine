
from dotenv import load_dotenv
import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


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



root_agent = LlmAgent(
    name="habit_analysis_agent",
    model=MODEL,
    instruction="""
You are a habit analysis assistant.

Use the 'analyse_habit' tool when the user asks you
to analyze a habit.

The tool requires:

- habit_name: Name of the habit to analyze.

Pass this argument to the tool accurately.
Use the tool's returned results as the basis for your analysis.
Explain the results clearly, and do not invent metrics or
claim that the tool returned information did not provide.

If the required input is missing, ask the user for it.
""",
    tools=[habit_processing_tools],
)

