                main.py
                   │
         ┌─────────┴─────────┐
         │                   │
      utils.py        Processors
                           │
                ┌──────────┴──────────┐
                │                     │
     binary_processing.py   numerical_processing.py

# Architecture

The project comprises three main components: main.py, utils.py, and the Processors package. 
Each component has a clearly defined responsibility. Together, they separate request handling,
shared utilities, and habit processing into dedicated components of the application. 

## main.py

Responsibilities:
- Handles API requests.
- Acts as the application's orchestrator.
- Coordinates the work performed by other modules.
- Determines the habit type using metadata.
- Delegates processing to the appropriate pipeline.
- Returns the final JSON response.

## utils.py

Responsibilities:
- Contains shared utility functions used across multiple modules.
- Centralizes common functionality to avoid code duplication.
- Allows other modules to focus on their primary responsibilities.

## Processors

The `Processors` package contains the application's business logic.
it comprises 2 independent processing pipelines:
- `binary_processing.py`
- `numerical_processing.py`
the pipelines are separated because they solve fundamentally different problems.
each pipeline encapsulates its own processing logic

### binary_processing.py

Responsibilities:
- Processes binary habits.
- Computes behavioral context.
- Computes performance metrics.

### numerical_processing.py

Responsibilities:
- Processes numerical habits. 
- Computes behavioral context.
- Computes performance metrics.

