import os
import dspy
from typing import List, Dict
import importlib.util

from utils import delete_json_key_val


class ComputeQuery(dspy.Signature):
    """
    Generate a code without any comments in it based on computation required by query.

    This signature generates a code without any comments in it based on the computation which the query is asking. The code should be such that it is running on a list of object where every object contains some fields which are explained in the 'dataset_fields' attribute.
    The code should access the fields which are required by the query and should use only those names in the code which are specified in the 'dataset_fields'. The name of function in the code should only be 'func' and not something else. Dont write anything outside the function.

    Attributes:
        query: A string representing the user's input query. This will contain some computation request which will have to be done by running a code on the dataset.
        dataset_fields: A list of fields which are in every single object with the description of each field.


        Example Inputs:
        1. Query: "What was the total amount spent last month?"
           dataset_fields: "[{"name": "name", "type": "string", "description":"name of the item"},{"name": "prices", "type": "float", "description":"price of the item"}, {"name": "date", "type": "string", "description":"date of purchase of the item"}]"
            - Output: def func(objects):
                        total_sum = 0
                        for obj in objects:
                          total_sum += obj.get("price", 0)  # Default to 0 if "price" is missing

                        return total_sum
        2. Query: "What was the average amount spent on electronics last month?"
           dataset_fields: "[{"name": "name", "type": "string", "description":"name of the item"},{"name": "prices", "type": "float", "description":"price of the item"}, {"name": "date", "type": "string", "description":"date of purchase of the item"}]"
            - Output: def func(objects):
                        total_sum = 0
                        total_products = len(objects)
                        for obj in objects:
                          total_sum += obj.get("price", 0)  # Default to 0 if "price" is missing

                        if total_products == 0:
                          return 0

                        return total_sum / total_products

        3. Query: "What is the difference in price between the last two headphones which i bought?"
           dataset_fields: "[{"name": "name", "type": "string", "description":"name of the item"},{"name": "prices", "type": "float", "description":"price of the item"}, {"name": "date", "type": "string", "description":"date of purchase of the item"}]"
            - Output: def func(objects):
                        if len(objects) < 2:
                          print("The list must have at least two objects.")
                          return None

                        price1 = objects[0].get("price", 0)  # Default to 0 if "price" is missing
                        price2 = objects[1].get("price", 0)
                        return abs(price1 - price2)
          To create a function to plot a graph, pie chart or something use matplotlib.
    """
    query: str = dspy.InputField(
        description="User's natural language query. Which contains a computation request")
    dataset_fields: List[Dict[str, str]] = dspy.InputField(
        description="List of dataset fields with their names and types and descriptions."
    )
    code: str = dspy.OutputField(
        description="Generated Python code without any comments in it with function named 'func' to compute the query using a list of objects where each object contain the given 'dataset_fields' .")


compute_query = dspy.ChainOfThought(ComputeQuery)
# query = "how much did I spend last month"
# dataset_fields = [{"name": "name", "type": "string", "description": "name of the item"}, {"name": "price", "type": "float",
#                                                                                           "description": "price of the item"}, {"name": "date", "type": "string", "description": "date of purchase of the item"}]

