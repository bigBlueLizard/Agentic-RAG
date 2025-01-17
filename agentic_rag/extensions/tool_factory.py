# from typing import List, Literal, Callable
# import requests


# class APIEndpoint:
#     def __init__(self, tool_url: str, tool_method: Literal["GET", "POST", "HEAD", "PUT", "DELETE"], tool_documentation: str, params: List[str]):
#         self.tool_url = tool_url
#         self.tool_method = tool_method
#         self.tool_documentation = tool_documentation
#         self.params = params


# def tool_factory(tools: List[APIEndpoint]) -> List[Callable[..., dict]]:
#     endpoint_functions = []

#     for tool in tools:
#         def endpoint_function(**kwargs):
#             """placeholder docstring."""
#             print("CALLING TOOL BRUHHH")
#             data = {k: v for k, v in kwargs.items() if k in tool.params}

#             missing_params = [
#                 param for param in tool.params if param not in data]
#             if missing_params:
#                 raise ValueError(
#                     f"Missing required parameters for {tool.tool_url}: {', '.join(missing_params)}")

#             try:
#                 if tool.tool_method == "GET":
#                     response = requests.get(tool.tool_url, params=data)
#                 elif tool.tool_method == "POST":
#                     response = requests.post(tool.tool_url, json=data)
#                 elif tool.tool_method == "HEAD":
#                     response = requests.head(tool.tool_url)
#                 elif tool.tool_method == "PUT":
#                     response = requests.put(tool.tool_url, json=data)
#                 elif tool.tool_method == "DELETE":
#                     response = requests.delete(tool.tool_url, json=data)
#                 else:
#                     raise ValueError(
#                         f"Unsupported HTTP method: {tool.tool_method}")

#                 response.raise_for_status()
#                 return response.json()
#             except requests.RequestException as e:
#                 print(f"Error with request to {tool.tool_url}: {e}")
#                 return None

#         endpoint_function.__doc__ = tool.tool_documentation

#         endpoint_functions.append(endpoint_function)

#     return endpoint_functions


# # tools = [
# #     # APIEndpoint("http://127.0.0.1:8000/products/search", "GET",
# #     #             "USE THIS TOOL ONLY WHEN THERE IS NEED TO SEARCH A PRODUCT.\nSearch products with multiple filtering and sorting options:\nPartial name search\nCategory filtering\nPrice range filtering\nStock availability filtering\nSorting by price, name, or stock\nPagination support", ["name", "category_id", "min_price", "max_price", "in_stock", "sort_by", "sort_order", "page", "page_size"]),
# #     # APIEndpoint("https://example.com/api/resource2", "GET",
# #     #             "Documentation for resource2", ["param1", "param2"]),
# # ]
# tools = [
#     APIEndpoint(
#         tool_url="http://127.0.0.1:8000/",
#         tool_method="GET",
#         tool_documentation="use this tool whenever you need to search up the product using these parameters.\nthe following is the request schema for this route:\n{'properties': {'id': {'type': 'integer', 'title': 'Id'}, 'name': {'type': 'string', 'title': 'Name'}, 'description': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'title': 'Description'}, 'price': {'type': 'number', 'title': 'Price'}, 'stock': {'type': 'integer', 'title': 'Stock'}, 'is_available': {'type': 'boolean', 'title': 'Is Available'}, 'category_id': {'type': 'integer', 'title': 'Category Id'}}, 'type': 'object', 'required': ['id', 'name', 'description', 'price', 'stock', 'is_available', 'category_id'], 'title': 'ProductResponse'}",
#         params=['name', 'category_id', 'min_price', 'max_price',
#                 "in_stock", "sort_by", "sort_order", "page", "page_size"]
#     )
# ]
# endpoint_functions = tool_factory(tools)
