import processing
import utils
import asyncio
import json
import sys

from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type



# mcp tool
def process_habit_csv(
    habit_csv_path: str,
    meta_csv_path: str,
    habit_name: str,
) -> dict: 
    """
    Process a habit using its habit data CSV, metadata CSV,
    and habit name.

    Args:
        habit_csv_path: Path to the CSV containing the selected
            habit's data.
        meta_csv_path: Path to the metadata CSV of habits.
        habit_name: Name of the habit to process.

    Returns:
    A JSON-safe dictionary containing two sections:
    'behavior_context' and 'metrics', each containing a dictionary.
    """
    meta_df = utils.load_data(meta_csv_path)
    habit_df = utils.load_data(habit_csv_path)

    #extract habit
    raw_df = habit_df[["Date", habit_name]]
    raw_df = raw_df.rename(columns={habit_name: "Value"}) #name based value passed to arguments

    # core capability
    result = processing.process_habits(
        meta_df,
        raw_df,
        habit_name
    )

    return result

# mcp schema
# Wrap as ADK FunctionTool
process_habit_tool = FunctionTool(process_habit_csv)






