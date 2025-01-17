import dspy
from pydantic import BaseModel, Field


class InputModel(BaseModel):
    query: str = Field(
        description="The user's query in natural language. This could include requests, commands, or questions.")


class OutputModel(BaseModel):
    needs_action: bool = Field(
        description="True if the query requires further processing or action beyond\ndata retrieval (e.g., invoking APIs, modifying state, or performing computations). \nFalse if only information retrieval is sufficient.")


class QueryActionSignature(dspy.Signature):
    """
    Determine if a query requires an action after data retrieval.

    This signature is used to classify user queries based on whether
    further actions (e.g., executing a command, modifying data, or invoking an API)
    are needed beyond simple data retrieval.

    Attributes:
        query: A string representing the user's input query. This could be a question,
               a command, or a request for specific data.
        needs_action: A boolean output that indicates if the query requires an actionable
                      response. True if an action (e.g., calculation, transformation,
                      API call) is needed; False if only information retrieval suffices.

    Example Inputs:
        1. "What's the weather in Paris?"
            - Output: False (information retrieval only)
        2. "Book me a flight to New York."
            - Output: True (action needed: flight booking)
        3. "Convert this amount to USD."
            - Output: True (action needed: currency conversion)
        4. "Show me the top headlines for today."
            - Output: False (simple retrieval of data)
    """
    input: InputModel = dspy.InputField()
    output: OutputModel = dspy.OutputField()
