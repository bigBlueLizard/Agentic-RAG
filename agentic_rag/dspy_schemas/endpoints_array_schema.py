from pydantic import BaseModel, Field
import dspy


class InputModel(BaseModel):
    documentation: str = Field(
        description="Documentation of different API endpoints and their response schemas.")
    query: str = Field(
        description="Query that has to be answered using the endpoints given in the documentation.")


class OutputModel(BaseModel):
    endpoints: list[str] = Field(
        description="Answer with a non-empty python array of endpoint URLs only that can possibly answer the query even if its vague. The length of the array should be exactly one. Take  the URLs from the documentation as it is, do not mutate them even slightly. You will be punished if you answer with an endpoint that is outside the given data or mutated.")
    # endpoints: list = Field(
    #     description="Extract the only endpoint that can answer the query. Respond with the URL only and respond such that it is a python array of only one element. meaning the response should look something like ['url here']")


class ArrayAnswerSignature(dspy.Signature):
    input: InputModel = dspy.InputField()
    output: OutputModel = dspy.OutputField()
