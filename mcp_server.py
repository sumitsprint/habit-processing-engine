import processing
import utils
import asyncio
import json


# mcp library
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ADK tools
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type



# mcp tool
def analyse_habit(
    habit_name: str
) -> dict: 
    """
    Analyse a habit using data retrieved from PostgreSQL.

    Args:
        
        habit_name: Name of the habit to process.

    Returns:
    A JSON-safe dictionary containing two sections:
    'behavior_context' and 'metrics', each containing a dictionary.
    """
    # fetch and process
    meta_df, raw_df = utils.fetch_habit_data(habit_name)
    
    # core capability
    result = processing.process_habit(
        meta_df,
        raw_df,
        habit_name
    )

    return result


# adk tool to expose
# 1. Prepare the ADK Tool
process_habit_tool_expose = FunctionTool(analyse_habit) # represent the python function as a  ADK tool. then mcp server exposes this tool
# google adk needs to understand and ineract with tools through an interface it supports

# 2. Create the MCP Server instance
app = Server("habit-processing-mcp")


# 3. Implement the list_tools handler
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    mcp_tool_schema = adk_to_mcp_tool_type(process_habit_tool_expose)
    return [mcp_tool_schema]

# 4. Implement the call_tool handler
@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    if name == process_habit_tool_expose.name:
        try:
            # Execute the ADK tool
            adk_tool_response = await process_habit_tool_expose.run_async(
                args=arguments, 
                tool_context=None,
            )
            # Format into MCP TextContent
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]
        except Exception as e:
            error_text = json.dumps({"error": str(e)})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        error_text = json.dumps({"error": f"Tool '{name}' not found."})
        return [mcp_types.TextContent(type="text", text=error_text)]


# 5. MCP Server Runner (Stdio)
async def run_mcp_stdio_server():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name, #
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )    


if __name__ == "__main__":
    asyncio.run(run_mcp_stdio_server())



# next step is adk agent 
# read documentation


