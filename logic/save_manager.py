import json
import os


def save_project(file_path, template_path, checked_paths):
    data = {
        "template_file": template_path,
        "checked_items": checked_paths
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_project(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
