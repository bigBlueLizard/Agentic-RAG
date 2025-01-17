import json
import requests
import pathway as pw
import os
from constants import CONTEXT_KEY, DATA_FOLDER, GEMINI_API_URL, REQUEST_HEADERS, THRESHOLD, GEMINI_API_KEY
from urllib.parse import urlparse

os.environ['GOOGLE_API_KEY'] = GEMINI_API_KEY


def generate_content_gemini(prompt, context):
    prompt = prompt.replace(CONTEXT_KEY, context)

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    response = requests.post(
        GEMINI_API_URL, headers=REQUEST_HEADERS, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"


def web_search_needed(scores: list):
    return min(scores) > THRESHOLD


def parse_duckduckgo_search_results(results):
    context = ""
    for i in results:
        context += i['body'] + "\n"
    return context


def get_response_schema(route: str):
    with open(DATA_FOLDER + f"/schemas/response/{route}/200.txt", "r") as f:
        res_schema = f.read()
    return res_schema


def get_request_schema(route: str):
    route = route.replace("2.3/", "")
    result = {
        "parameters": "",
        "body": ""
    }
    parsed_url = urlparse(route)
    with open(DATA_FOLDER + f"/schemas/request{parsed_url.path.rstrip('/')}/parameters.txt", "r") as f:
        result['parameters'] = f.read()

    try:
        with open(DATA_FOLDER + f"/schemas/request{parsed_url.path.rstrip('/')}/req_schema.txt", "r") as f:
            result['body'] = f.read()
    except:
        pass

    return result


def delete_json_key_val(json_data, paths: list):

    def convert_slash_to_dot_with_hash(paths):
        result = []
        for path in paths:
            if not isinstance(path, str) or path.strip() == "":
                result.append("")
                continue
            if path.startswith("#"):
                result.append("#" + path[1:].replace("/", "."))
            else:
                result.append(path.replace("/", "."))
        return result

    def find_and_delete(obj, path_parts):
        if not path_parts:
            return False

        current_key = path_parts[0]

        if len(path_parts) == 1:
            if isinstance(obj, dict) and current_key in obj:
                del obj[current_key]
                return True
            elif isinstance(obj, list) and current_key.isdigit():
                index = int(current_key)
                if 0 <= index < len(obj):
                    obj.pop(index)
                    return True
        else:
            if isinstance(obj, dict) and current_key in obj:
                return find_and_delete(obj[current_key], path_parts[1:])
            elif isinstance(obj, list) and current_key.isdigit():
                index = int(current_key)
                if 0 <= index < len(obj):
                    return find_and_delete(obj[index], path_parts[1:])
        return False

    def search_and_delete(json_data, path_parts):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key == path_parts[0]:
                    if find_and_delete(json_data, path_parts):
                        return True
                if isinstance(value, (dict, list)):
                    if search_and_delete(value, path_parts):
                        return True
        elif isinstance(json_data, list):
            for item in json_data:
                if isinstance(item, (dict, list)):
                    if search_and_delete(item, path_parts):
                        return True
        return False

    def process_and_delete_dynamic(json_data, slash_paths):
        dot_paths = convert_slash_to_dot_with_hash(slash_paths)

        for dot_path in dot_paths:
            normalized_path = dot_path[2:] if dot_path.startswith(
                "#.") else dot_path
            path_parts = normalized_path.split(".")
            search_and_delete(json_data, path_parts)

        return json_data

    updated_json = process_and_delete_dynamic(json_data, paths)

    return updated_json
