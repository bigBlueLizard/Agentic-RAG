import dspy
from pydantic import BaseModel, Field

class InputModel(BaseModel):
    query: str = Field(
        description="The user's query in natural language. This could include requests, commands, or questions."
        )


class OutputModel(BaseModel):
    follow_up: list[str] = Field(
        description=(            
            "A list containing 3 strings that represent the top 3 most likely similar actions or queries the user might independently ask next, "
            "related to the original query but not extending it directly."
            ))


class FollowUpSignature(dspy.Signature):
      """
    Generate the top 3 most relevant and related similar actions or queries that a user might ask next, based on the given query.

    Similar actions should:
    - Be related to the user's input query but should not directly extend it.
    - Be framed as independent actions or questions the user might naturally follow up with.
    - Match the type of the input query (e.g., data retrieval queries should produce similar data retrieval follow-ups; action queries should suggest similar action follow-ups).

    Ensure that:
    - The follow-up queries represent what **the user is most likely to ask next**, not what the chatbot should respond with.
    - Each follow-up is contextually relevant but distinct enough from the original query.

    Attributes:
        query: A string representing the user's input query. This could be a question, a command, or a request for specific data.
        follow_up_questions: A list of 3 strings representing the top 3 most likely related queries or actions the user might ask next.

    Example Inputs and Outputs:
        1. "Place an order of iPhone."
            - Output: ["Place an order of an iPhone charger", "Place an order of iPhone cover.", "Place an order of Airpods."]
        2. "What is the total cost of products in my cart?"
            - Output: ["Which is the most expensive thing in my cart?", "Which is the least expensive thing in my cart?", "Is there anything in my cart that is out of stock?"]
        3. "Write a review for this product."
            - Output: ["Reorder the product", "Return the product", "Search for similar products."]
        4. "Write a bad review on my last order."
            - Output: ["Request a refund for the order.", "Contact customer support about the issue.", "Write another review for a different product."]
    """
      input: InputModel = dspy.InputField()
      output: OutputModel = dspy.OutputField()
