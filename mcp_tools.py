import utils
import processing
from pathlib import Path


# python function perform the work
# returns a list[dict] of habit names and types {"name": "habit_name", "type": "habit_type"}
def list_habits() -> list[dict]:
    """Return all available habit names with their types from the database."""
    return utils.fetch_habit_names()
    

# python function perform the work
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

DOCS_DIR = Path(__file__).parent / "docs"

def get_habit_docs(habit_type: str) -> dict:
    """
    Retrieve the complete domain documentation (field glossary and pipeline mechanics)
    for a specified habit type.

    Args:
        habit_type: The habit category. Must be either 'YES_NO' or 'NUMERICAL'.

    Returns:
        A dictionary containing the output fields definitions and processing mechanics.
    """
    if habit_type not in ["YES_NO", "NUMERICAL"]:
        return "Invalid habit type. Must be 'YES_NO' or 'NUMERICAL'."

    elif habit_type == "YES_NO":
        processing_path = DOCS_DIR / "binary_processing.md"
        fields_path = DOCS_DIR / "binary_output_fields.md"

    elif habit_type == "NUMERICAL":
        processing_path = DOCS_DIR / "numerical_processing.md"
        fields_path = DOCS_DIR / "numerical_output_fields.md"

    # convert content to string  

    fields_content = fields_path.read_text(encoding="utf-8") if fields_path.exists() else "Field documentation not found."
    processing_content = processing_path.read_text(encoding="utf-8") if processing_path.exists() else "Processing documentation not found."

    return {
        "habit_type": habit_type,
        "fields_definitions": fields_content,
        "pipeline_mechanics": processing_content
    }


    
    
    