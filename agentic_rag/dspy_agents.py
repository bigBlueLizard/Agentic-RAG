import time
import dspy
import requests
from dspy_schemas.code_generator_schema import ComputeQuery
from dspy_schemas.context_qa_schema import ContextQuestionSignature
from dspy_schemas.endpoints_array_schema import ArrayAnswerSignature
from dspy_schemas.rephraser_schema import QueryRephraseSignature
from dspy_schemas.request_schema_agent import RequestSchemaGeneratorSignature
from dspy_schemas.response_generator import GenerateResponse, GenerateResponseUsingCodeOutput, GenerateResponseWithoutCodeOutput
from dspy_schemas.follow_up import FollowUpSignature
from dspy_schemas.action_schema import QueryActionSignature

# # lm = GeminiLM("gemini-pro", temperature=0.6)
lm = dspy.LM('groq/gemma2-9b-it',api_key='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')
# lm = dspy.LM('gemini/gemini-1.5-flash',api_key="AIzaSyCLH-xZjLz0sDmFlpOXVe2yUcg8sEIq2Vc")
# lm = dspy.LM('ollama_chat/qwen:0.5b', api_base='http://localhost:11434', api_key='')
# lm = dspy.LM('openai/gpt-3.5-turbo', api_key='')
# lm = dspy.LM('openai/gpt-4o', api_key='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')
# lm = dspy.LM('cohere/command-r-plus', api_key='G7XVJRHpH2CP8jfj8k5WjU6BiXGJclTgRN3fkOnK')
dspy.configure(lm=lm)
# https://api.stackexchange.com/2.3/
# {"key":"U4DMV*8nvpm3EOpvf69Rxw((", "access_token":"eIbJRxEKykylIi6r03*1cA))"}
# sync token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxMjM4LCJuYW1lIjoiS29udnV4IiwiZW1haWwiOiJrb252dXg0QGdtYWlsLmNvbSIsInNpZ25fdXBfbWV0aG9kIjoiZ29vZ2xlIiwic2lnbl91cF9kYXRlIjoiMjAyNC0xMS0yN1QxNjoxMDo1NC4yOTc4MzYiLCJwZnAiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NLeDE3bmg1ejA0Qm9la3JocUMybG5hUTZfR0xzZ3B3aHhaRGE2VGpMa0swVXNScUE9czk2LWMiLCJhZG1pbiI6ZmFsc2UsImFjY2VzcyI6MCwicGxhbl9pZCI6bnVsbH0sImlhdCI6MTczMjcyMzg1NX0.Kc_2aeBHeObUDGFcGUhUuNcRkPOxmXzjUrnIdqpOz7g"
# api base = "https://sync2cal.up.railway.app/"


class Logger:
    def __init__(self, logged_agents=None):
        self.logs = {}
        self.total_cost = 0
        self.total_tokens = 0
        self.total_time = 0
        self.logged_agents = set(logged_agents) if logged_agents else None

    def add_log(self, agent_name, cost, tokens, duration, messages, outputs):
        if self.logged_agents and agent_name not in self.logged_agents:
            return

        if agent_name not in self.logs:
            self.logs[agent_name] = []
        self.logs[agent_name].append({
            'cost': cost,
            'tokens': tokens,
            'time': duration,
            'messages': messages,
            'outputs': outputs
        })
        self.total_cost += cost or 0
        self.total_tokens += tokens or 0
        self.total_time += duration

    def show_logs(self):
        if not self.logs:
            print("No logs recorded yet.")
            return

        for agent_name, logs in self.logs.items():
            print(f"\nAgent: {agent_name}")
            for entry in logs:
                print(f"Cost: {entry['cost']}")
                print(f"Tokens: {entry['tokens']}")
                print(f"Time: {entry['time']} seconds")
                print("\nMessages:")
                for msg_idx, message in enumerate(entry['messages'], 1):
                    print(f"  [{msg_idx}] {message}")
                print("\nOutputs:")
                for out_idx, output in enumerate(entry['outputs'], 1):
                    print(f"  [{out_idx}] {output}")

    def clear_logs(self):
        self.logs = {}
        self.total_cost = 0
        self.total_tokens = 0
        self.total_time = 0


class DSPYAgent(dspy.Predict):
    def __init__(self, signature, logger, name, _parse_values=True, callbacks=None, **config):
        super().__init__(signature, _parse_values, callbacks, **config)
        self.logger = logger
        self.name = name

    def __call__(self, *args, **kwargs):
        start_time = time.time()
        result = super().__call__(*args, **kwargs)
        end_time = time.time()

        cost = 0
        tokens = 0
        time_taken = end_time - start_time
        messages = []
        outputs = []
        for last_call in lm.history:
            cost += last_call.get('cost') or 0
            tokens += last_call['usage'].get('total_tokens') or 0
            messages.extend([message['content']
                            for message in last_call['messages']])
            outputs.extend(last_call['outputs'])

        lm.history.clear()
        self.logger.add_log(self.name, cost, tokens,
                            time_taken, messages, outputs)

        return result


class TooledDSPYAgent(dspy.ReAct):
    def __init__(self, signature, tools, max_iters=3, logger=None, name="DefaultAgent"):
        super().__init__(signature, tools, max_iters)
        self.logger = logger
        self.name = name

    def __call__(self, *args, **kwargs):
        start_time = time.time()
        result = super().__call__(*args, **kwargs)
        end_time = time.time()

        cost = 0
        tokens = 0
        time_taken = end_time - start_time
        messages = []
        outputs = []
        for last_call in lm.history:
            cost += last_call.get('cost') or 0
            tokens += last_call['usage'].get('total_tokens') or 0
            messages.extend([message['content']
                            for message in last_call['messages']])
            outputs.extend(last_call['outputs'])

        lm.history.clear()
        self.logger.add_log(self.name, cost, tokens,
                            time_taken, messages, outputs)

        return result


# tools = [
#     APIEndpoint(
#         tool_url="http://127.0.0.1:8000/products/search",
#         tool_method="GET",
#         tool_documentation="use this tool whenever you need to search up the product using these parameters or if you wanna find the product id for a request schema.\nthe following is the request schema for this route:\n{'properties': {'id': {'type': 'integer', 'title': 'Id'}, 'name': {'type': 'string', 'title': 'Name'}, 'description': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'title': 'Description'}, 'price': {'type': 'number', 'title': 'Price'}, 'stock': {'type': 'integer', 'title': 'Stock'}, 'is_available': {'type': 'boolean', 'title': 'Is Available'}, 'category_id': {'type': 'integer', 'title': 'Category Id'}}, 'type': 'object', 'required': ['id', 'name', 'description', 'price', 'stock', 'is_available', 'category_id'], 'title': 'ProductResponse'}",
#         params=['name', 'category_id', 'min_price', 'max_price',
#                 "in_stock", "sort_by", "sort_order", "page", "page_size"]
#     )
# ]
# tool_callables = tool_factory(tools=tools)







def search_product(name: str):
    """
    search a product by its name.
    the response contains an array of search results.
    The following is the format of the response:
    {'properties': {'id': {'type': 'integer', 'title': 'Id'}, 'name': {'type': 'string', 'title': 'Name'}, 'description': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'title': 'Description'}, 'price': {'type': 'number', 'title': 'Price'}, 'stock': {'type': 'integer', 'title': 'Stock'}, 'is_available': {'type': 'boolean', 'title': 'Is Available'}, 'category_id': {'type': 'integer', 'title': 'Category Id'}}, 'type': 'object', 'required': ['id', 'name', 'description', 'price', 'stock', 'is_available', 'category_id'], 'title': 'ProductResponse'}
    If the query requires a product ID for its request schema, this tool is the best
    """
    print("Searching for ", name)
    return requests.get(f"http://127.0.0.1:8000/products/search?name={name}").json()
















# def search_calendar(name: str):
#     """
#     search for a calendar
#     whenever you need an id or a uuid
#     the name should be what a user would naturally type in the search field of a website
#     use this tool with only 1 word in the name
#     """
#     print("Executing Tool for searching calendar : ", name)
#     return requests.get(f"https://sync2cal.up.railway.app/categories/search?query={name.split(' ')[0]}").json()


logger = Logger()
answer_from_context_agent = DSPYAgent(
    ContextQuestionSignature, logger=logger, name='agent basic')

endpoint_array_generator = DSPYAgent(
    ArrayAnswerSignature, logger=logger, name='agent filterer')

query_rephrase_agent = DSPYAgent(
    QueryRephraseSignature, logger=logger, name='agent rephraser')

generate_response_agent = DSPYAgent(
    GenerateResponse, logger=logger, name="response generator")  # gonna get outdated soon

code_generator_agent = DSPYAgent(ComputeQuery, logger=logger, name='code gen agent')

generate_response_using_code_output = DSPYAgent(
    GenerateResponseUsingCodeOutput, logger=logger, name='generate response using code ouptut')

generate_response_without_code_output = DSPYAgent(
    GenerateResponseWithoutCodeOutput, logger=logger, name='generate response without code ouptut')

generate_request_agent = TooledDSPYAgent(
    RequestSchemaGeneratorSignature, logger=logger, name='agent request generator', tools=[search_product])

follow_up_questions_agent = DSPYAgent(
    FollowUpSignature, logger=logger, name='follow up questions generator')

query_action_agent = DSPYAgent(QueryActionSignature,
                         logger=logger, name='action decider agent')

# tools_agent = DSPYAgent(ToolsAgentSignature, logger=logger,
#                         name="tools selector agent")

# claim_agent = DSPYAgent(
#     ClaimsAgentSignature, logger=logger, name='agent breakdown')
