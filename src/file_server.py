from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import os

app = FastAPI()


class FileMap:
    def __init__(self):
        self.root_folder_id = None
        self.file_map = {}


def walk(dir: Path, root_dir_id, root_folder_name, file_map: FileMap):
    for child in dir.iterdir():

        parent_stats = os.stat(dir)
        parent_id = f"{parent_stats.st_dev}-{parent_stats.st_ino}"

        child_stats = os.stat(child)
        child_id = f"{child_stats.st_dev}-{child_stats.st_ino}"

        if child.is_dir():
            if child_id not in file_map.file_map:
                file_map.file_map[child_id] = {
                    "id": child_id,
                    "name": child.name,
                    "is_dir": True,
                    "children_ids": [],
                    "full_path": str(child)
                }
                if child_id != parent_id:
                    file_map.file_map[child_id]["parent_id"] = parent_id

            if parent_id not in file_map.file_map:
                file_map.file_map[parent_id] = {
                    "id": parent_id,
                    "name": root_folder_name if parent_id == root_dir_id else child.name,
                    "is_dir": True,
                    "children_ids": [child_id],
                    "full_path": str(dir)
                }
            else:
                file_map.file_map[parent_id]["children_ids"].append(child_id)

            walk(child, root_dir_id, root_folder_name, file_map)

        elif child.is_file():
            if parent_id not in file_map.file_map:
                file_map.file_map[parent_id] = {
                    "id": parent_id,
                    "name": root_folder_name if parent_id == root_dir_id else child.name,
                    "is_dir": True,
                    "children_ids": [child_id],
                    "full_path": str(dir)
                }
            else:
                file_map.file_map[parent_id]["children_ids"].append(child_id)

            file_map.file_map[child_id] = {
                "id": child_id,
                "name": child.name,
                "parent_id": parent_id,
                "size": child_stats.st_size,
                "mod_date": child_stats.st_mtime,
                "full_path": str(child)
            }


def walk_directory(dir: str, root_folder_name: str) -> FileMap:
    root_dir = Path(dir).resolve()
    root_dir_stats = os.stat(root_dir)
    root_dir_id = f"{root_dir_stats.st_dev}-{root_dir_stats.st_ino}"

    file_map = FileMap()
    file_map.root_folder_id = root_dir_id

    walk(root_dir, root_dir_id, root_folder_name, file_map)

    return file_map


@app.post("/filesystem")
async def filesystem(request: Request):
    data = await request.json()
    path_to_walk = data["path"]
    root_folder_name = data["path"]

    if not Path(path_to_walk).exists():
        return {"error": "Path does not exist"}

    files = walk_directory(path_to_walk, root_folder_name)
    print(files.__dict__)
    return files.__dict__


@app.post("/filesystem/download")
async def download(request: Request):
    data = await request.json()

    requested_files = data
    if len(requested_files) > 1:
        # Here we might want to implement a zipping functionality
        # but this is a more complex task. For now, we'll just return an error.
        return {"error": "Zipping multiple files not yet implemented."}
    else:
        return FileResponse(requested_files[0]["full_path"])
