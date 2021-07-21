import prefect
from prefect.storage.docker import Docker
from pathlib import Path
import os
def find_all_python_files(path):
    ignore_directories = ["__pycache__", ".venv", ".git", ".vscode"]
    python_files = []
    for element in os.listdir(path):
        if os.path.isdir(os.path.join(path, element)):
            if element not in ignore_directories:
                python_files.extend(find_all_python_files(os.path.join(path, element)))
        else:
            if element.endswith(".py"):
                python_files.append(os.path.join(path, element))
    return python_files


def compile_helper_files_dict(paths):
    helper_paths = {}
    for path in paths:
        source_file_path = path

        dest_file_path = Path(path).relative_to(Path.cwd())
        dest_file_path_string = str(dest_file_path)
        helper_paths[source_file_path] = "modules/" + dest_file_path_string
    return helper_paths


all_python_files = find_all_python_files(Path.cwd())
helper_files = compile_helper_files_dict(all_python_files)

storageObj = Docker(
    dockerfile="Dockerfile",
    registry_url=DOCKER_REGISTRY_URL,
    env_vars={
        "PYTHONPATH": "$PYTHONPATH:modules/",
    },
    files=helper_files,
)
