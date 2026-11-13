from google.adk import Agent
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

# MCP tools
from mcp_tools import list_habits, analyse_habit, get_habit_docs


# 1. Prepare the ADK Tool
process_habit_tool_expose = FunctionTool(analyse_habit) 
list_habits_tool_expose = FunctionTool(list_habits) 
get_habit_documentation_tool_expose = FunctionTool(get_habit_docs)

# 2. Create the MCP Server instance
app = Server("habit-processing-mcp")


# 3. Implement the list_tools handler
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    mcp_tool_schema_process_habit = adk_to_mcp_tool_type(process_habit_tool_expose)
    mcp_tool_schema_list_habits = adk_to_mcp_tool_type(list_habits_tool_expose)
    mcp_tool_schema_get_habit_documentation = adk_to_mcp_tool_type(get_habit_documentation_tool_expose)
    return [mcp_tool_schema_process_habit, mcp_tool_schema_list_habits, mcp_tool_schema_get_habit_documentation]

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
    elif name == list_habits_tool_expose.name:
        try:
            # Execute the ADK tool
            adk_tool_response = await list_habits_tool_expose.run_async(
                args=arguments, 
                tool_context=None,
            )
            # Format into MCP TextContent
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]
        except Exception as e:
            error_text = json.dumps({"error": str(e)})
            return [mcp_types.TextContent(type="text", text=error_text)]  
    elif name == get_habit_documentation_tool_expose.name:
        try:
            # Execute the ADK tool
            adk_tool_response = await get_habit_documentation_tool_expose.run_async(
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
                server_name=app.name, 
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )    


if __name__ == "__main__":
    asyncio.run(run_mcp_stdio_server())


# what is loop agent and how it is different from llm agent


# next step is adk agent 
# read documentation


# 1. Agent receives tool descriptions
#             |

# Learns that list_habits is available.
                # |

# 2. Agent requests a tool call

# name = "list_habits"

# 3. MCP server receives the request

# call_mcp_tool(name, arguments)

# 4. Your code matches the name

# name == list_habits_tool_expose.name

# 5. ADK executes the wrapped function

# list_habits_tool_expose.run_async(...)