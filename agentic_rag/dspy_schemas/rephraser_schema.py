from pydantic import BaseModel, Field
import dspy


class InputModel(BaseModel):
    query: str = Field(description="Query to be rephrased")


class OutputModel(BaseModel):
    rephrased_query: str = Field(
        description="Rephrase the user's query into a succinct statement suitable for documentation in an API they are using, emphasizing clarity and brevity.")


class QueryRephraseSignature(dspy.Signature):
    input: InputModel = dspy.InputField()
    output: OutputModel = dspy.OutputField()
