from pydantic import BaseModel, Field
import dspy


class InputModel(BaseModel):
    request_parameters_schema: str = Field(
        description="Define the parameters required for the request as a query. Use this schema specifically to extract and structure the request parameters content in the final output."
    )
    request_body_schema: str = Field(
        description="Provide the schema for the request body. This will be used to extract and structure only the request body content in the final output."
    )
    query: str = Field(
        description="The input query from which the request parameters and request body will be extracted. Ensure that all relevant details for both are captured accurately."
    )


class OutputModel(BaseModel):
    request_parameters: dict = Field(
        description="A JSON object containing the request parameters with values derived from the query. If a request parameters schema is provided, ensure this output is never empty. Include only values explicitly mentioned in the query—do not add anything extra."
    )
    request_body: dict = Field(
        description="A JSON object containing the request body with values derived from the query. If a request body schema is provided, this output must never be empty. Include only values explicitly mentioned in the query—do not add anything extra."
    )


class RequestSchemaGeneratorSignature(dspy.Signature):
    input: InputModel = dspy.InputField()
    output: OutputModel = dspy.OutputField()
