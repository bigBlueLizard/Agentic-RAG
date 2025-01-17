import yaml
import json
from pathlib import Path


def converter(filepath: str):
    filepath = Path(filepath).resolve()
    if not filepath.is_file():
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")

    output_dir = filepath.parent / "json_converted"
    output_dir.mkdir(parents=True, exist_ok=True)

    with filepath.open("r") as f:
        data = yaml.safe_load(f)
    json_object = json.dumps(data, indent=4)
    json_file_name = filepath.stem + ".json"
    newfile = output_dir / json_file_name

    with newfile.open("w") as f:
        f.write(json_object)
