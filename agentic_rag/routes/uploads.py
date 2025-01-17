from fastapi import APIRouter, UploadFile, File
import os
from pathlib import Path
import json
from constants import CLEANED_DATA_FOLDER, DATA_FOLDER

upload_router = APIRouter()


def find_key(data, key):
    stack = [data]
    while stack:
        top = stack.pop()
        if isinstance(top, dict):
            if key in top:
                return top[key]
            for value in top.values():
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(top, list):
            stack.extend(top)
    return None


def clear_directory(directory_path: Path) -> None:
    """Recursively deletes all files and directories within the specified directory."""
    for item in Path(directory_path).glob("*"):
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            clear_directory(item)
            item.rmdir()


@upload_router.post("/upload_openapi")
async def openapi(file: UploadFile = File(...)):

    schemas_dir = Path(DATA_FOLDER + "/schemas")
    documentation_dir = Path(CLEANED_DATA_FOLDER)

    clear_directory(schemas_dir)
    clear_directory(documentation_dir)

    schemas_dir.mkdir(exist_ok=True, parents=True)
    documentation_dir.mkdir(exist_ok=True, parents=True)

    content = await file.read()
    data = json.loads(content)
    json.dump(data, open("openapi.json", "w"))
    routes = data['paths']
    response_schemas_path = Path(DATA_FOLDER + "/schemas/response")
    request_schemas_path = Path(DATA_FOLDER + "/schemas/request")
    response_schemas_path.mkdir(exist_ok=True, parents=True)
    request_schemas_path.mkdir(exist_ok=True, parents=True)

    for route in routes:
        route_path = Path(CLEANED_DATA_FOLDER + f"{route}")
        route_path.mkdir(exist_ok=True, parents=True)
        route_content = routes[route]
        request_type = "get"
        if route_content.get("post") is not None:
            request_type = "post"
        request_content = route_content.get(request_type)
        if request_content is not None:
            request_file_path = route_path.joinpath(f"{request_type}.txt")
            with open(request_file_path, "w") as f:
                f.write(str(request_content.get("description")))

            responses = request_content.get("responses")
            for i in responses:
                response_schema_description_path = response_schemas_path.joinpath(
                    f"{route[1:]}")
                response_schema_description_path.mkdir(
                    exist_ok=True, parents=True)
                with open(response_schema_description_path.joinpath(f"{i}.txt"), "w") as f:
                    current_response = responses.get(i)
                    schema_path = find_key(current_response, "$ref")
                    if schema_path:
                        schema_name = schema_path.split("/")[-1]
                        schema = data['components']['schemas'].get(schema_name)
                        if schema:
                            f.write(str(schema))
                    else:
                        f.write("No schema reference found.")

            request_schema_description_path = request_schemas_path.joinpath(
                f"{route[1:]}")
            request_schema_description_path.mkdir(exist_ok=True, parents=True)
            request_body = request_content.get('requestBody')
            if request_body:
                schema_path = find_key(request_body, "$ref")
                if schema_path:
                    schema_name = schema_path.split("/")[-1]
                    schema = data['components']['schemas'].get(schema_name)
                    if schema:
                        with open(request_schema_description_path.joinpath("req_schema.txt"), "w") as f:
                            f.write(str(schema))
                    else:
                        with open(request_schema_description_path.joinpath("req_schema.txt"), "w") as f:
                            f.write("No schema reference found.")
                else:
                    with open(request_schema_description_path.joinpath("req_schema.txt"), "w") as f:
                        f.write("No schema reference found.")

            query_params = ""
            parameters = request_content.get("parameters")
            if parameters:
                for parameter in parameters:
                    if parameter['in'] == 'query':
                        query_params += str(parameter)

            with open(request_schema_description_path.joinpath("parameters.txt"), "w") as f:
                f.write(query_params)

    return routes
