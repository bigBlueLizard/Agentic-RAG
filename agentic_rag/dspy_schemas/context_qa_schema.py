import dspy
from pydantic import BaseModel, Field


class InputModel(BaseModel):
    context: str = Field(description="Context for the question")
    question: str = Field(
        description="Question to be answered strictly from the above context")


class OutputModel(BaseModel):
    answer: str = Field(
        description="Answer to the question should be very strictly based on the context")


class ContextQuestionSignature(dspy.Signature):
    input: InputModel = dspy.InputField()
    output: OutputModel = dspy.OutputField()
