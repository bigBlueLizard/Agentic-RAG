import importlib
import importlib.util
import os
from fastapi import HTTPException
from urllib.parse import urlparse, urlunparse
from fastapi import APIRouter, Body
import requests
from constants import HOST, PORT
from extensions.pathway_client import PathwayVectorClient
# from extensions.tool_factory import APIEndpoint, tool_factory
from utils import delete_json_key_val, get_request_schema, get_response_schema
from dspy_agents import (
    query_rephrase_agent,
    endpoint_array_generator,
    generate_request_agent,
    generate_response_agent,
    query_action_agent,
    generate_response_without_code_output,
    generate_response_using_code_output,
    code_generator_agent
)
from dspy_schemas.endpoints_array_schema import InputModel as EndpointsArrayAgentInputSchema

from dspy_schemas.rephraser_schema import InputModel as RephraserAgentInputModel
from dspy_schemas.request_schema_agent import InputModel as RequestSchemaAgentInputModel
from dspy_schemas.action_schema import InputModel as ActionAgentInputModel
from dspy_agents import logger
import time

query_router = APIRouter()
client = PathwayVectorClient(host=HOST, port=PORT)


def helper(query, retrieved_data, dataset_fields):
    response = code_generator_agent(query=query, dataset_fields=dataset_fields)
    code_lines = response.code.splitlines()  # Split into lines
    if (code_lines[0] == "```python"):
        trimmed_code = "\n".join(code_lines[1:-1])
    else:
        trimmed_code = "\n".join(code_lines[0:])

    trimmed_script_path = "./content/trimmed_generated_code.py"
    with open(trimmed_script_path, 'w') as trimmed_file:
        trimmed_file.write(trimmed_code)

    exec(open(trimmed_script_path).read())

    script_path = "./content/trimmed_generated_code.py"
    spec = importlib.util.spec_from_file_location(
        "generated_code", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    updated_data = delete_json_key_val(
        json_data=retrieved_data, paths=dataset_fields)
    result = module.func(updated_data)
    # os.remove(script_path)
    return result


def solver(query, dataset_fields, retrieved_data):
    result = query_action_agent(input=ActionAgentInputModel(
        query=query
    ))
    decision = result.output.needs_action
    if decision == True:
        print("Action Required")
        help = helper(query, retrieved_data, dataset_fields)
        if help == None:
            print("no help ma chudao")
            answer = generate_response_without_code_output(query=query)
            return answer.response
        else:
            answer = generate_response_using_code_output(
                query=query, answer=help)
            return answer.response
    if decision == False:
        print("Action Not Required")
        answer = generate_response_agent(
            query=query, api_response=retrieved_data)

    return answer.response


def validate_headers(headers: dict):
    if not headers:
        raise HTTPException(status_code=400, detail="Token header is required")


def rephrase_query(query: str) -> str:
    rephrased = query_rephrase_agent(
        input=RephraserAgentInputModel(query=query))
    return rephrased.output.rephrased_query


def retrieve_docs(rephrased_query: str):
    return client.similarity_search_with_score(rephrased_query, k=3)


def parse_docs_to_endpoints(API_BASE: str, docs):
    documentation = ""
    results = {}

    for doc in docs:
        file_path = doc[0].metadata['path']
        route = "/".join(file_path.split("/")[1:-1])
        endpoint_url = f"{API_BASE}{route}"
        request_method = file_path.split("/")[-1].split('.')[0].upper()

        if doc[0].page_content != "None":
            doc_content = f'Endpoint URL: {endpoint_url}: {doc[0].page_content}'
            schema = get_response_schema(route)
            documentation += doc_content + \
                f"\nResponse Schema of {route}\n" + schema + "\n"
            results[endpoint_url] = {
                "response_schema": schema,
                "documentation": doc[0].page_content,
                "method": request_method
            }

    return documentation, results


def generate_endpoint_requests(rephrased_query: str, endpoints, results):
    reqs = []

    for endpoint in endpoints:
        request_schema = get_request_schema(endpoint)
        request_schema_generated = generate_request_agent(input=RequestSchemaAgentInputModel(
            request_parameters_schema=request_schema['parameters'],
            request_body_schema=request_schema['body'],
            query=rephrased_query
        ))
        parsed_url = urlparse(endpoint)
        url = urlunparse(
            (parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        reqs.append({
            'parameters': request_schema_generated.output.request_parameters,
            'body': request_schema_generated.output.request_body,
            'url': endpoint,
            'method': results[str(url)]['method']
        })

    return reqs


def execute_requests(reqs, headers):
    responses = []

    for request in reqs:
        url = request.get('url')
        method = request.get('method')
        params = request.get('parameters', {})
        body = request.get('body', {})
        print("executing request for ", url)
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(
                url, json=body, params=params, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(
                url, json=body, params=params, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        print("executed request for ", url)
        responses.append(response)

    return responses


def aggregate_responses(endpoints, reqs, responses):
    return {
        "endpoints": endpoints,
        "documentation_details": reqs,
        "responses": [response.json() for response in responses]
    }


metrics = []
APPROVAL_REQUIRED = ["http://127.0.0.1:8000/cart/add",
                     "http://127.0.0.1:8000/orders/place", "http://127.0.0.1:8000/reviews/post"]


@query_router.post("/retrieve")
async def retrieve_relevant(API_BASE: str, query: str, headers: dict = Body(...), approval_bypass=False):
    global metrics

    start_time = time.time()
    validate_headers(headers)

    rephrased_query = rephrase_query(query)
    docs = retrieve_docs(rephrased_query)
    documentation, results = parse_docs_to_endpoints(API_BASE, docs)

    relevant_endpoints = endpoint_array_generator(input=EndpointsArrayAgentInputSchema(
        query=rephrased_query,
        documentation=documentation
    ))
    endpoints = relevant_endpoints.output.endpoints

    reqs = generate_endpoint_requests(rephrased_query, endpoints, results)

    exec_start_time = time.time()
    for e in endpoints:
        if e in APPROVAL_REQUIRED and approval_bypass == False:
            return {
                'rag_response': 'The action you are attempting requires approval. More information in the approval dialog.',
                'documents': endpoints,
                'approval_required': True
            }

    responses = execute_requests(reqs, headers)
    exec_end_time = time.time()

    documents_for_agent = aggregate_responses(endpoints, reqs, responses)
    # print(documents_for_agent)
    final_response = generate_response_agent(
        query=query,
        api_response=documents_for_agent['responses']
    )

    end_time = time.time()
    exec_time = exec_end_time - exec_start_time
    total_time = end_time - start_time
    latency = total_time - exec_time

    query_metrics = {
        'token_usage': logger.total_tokens,
        'cost': logger.total_cost,
        'latency': latency,
        'retrieved_endpoints': endpoints,
        'agent_outputs': {}
    }
    query_metrics['agent_outputs'] = {}
    for agent_name, logs in logger.logs.items():
        query_metrics['agent_outputs'][agent_name] = [
            entry['outputs'] for entry in logs
        ]
    # print(query_metrics)
    metrics.append(query_metrics)

    logger.clear_logs()

    # data = solver(rephrased_query, [
    #     {
    #         "name": "order_id",
    #         "type": "integer",
    #         "description": "id of the order"
    #     },
    #     {
    #         "name": "status",
    #         "type": "string",
    #         "description": "current status of the order"
    #     },
    #     {
    #         "name": "total_amount",
    #         "type": "integer",
    #         "description": "total cost of the order"
    #     },
    #     {
    #         "name": "created_at",
    #         "type": "datetime %Y-%m-%dT%H:%M:%S.%f",
    #         "description": "date and time when the order was placed"
    #     },
    #     {
    #         "name": "items",
    #         "type": "list",
    #         "description": "array of products purchased in this order"
    #     },
    # ], documents_for_agent['responses'][0])
    data = final_response.response
    return {
        'rag_response': data,
        'documents': documents_for_agent,
        'query_metrics': query_metrics,
        'approval_required': False
    }


@query_router.get("/metrics")
async def get_metrics(index: int):
    return metrics[index]
