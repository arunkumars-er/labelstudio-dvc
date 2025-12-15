# Label Studio → YOLO export script
# Just run: python src/labelstudio/export_to_yolo.py

import os
import json
import shutil
import logging
from tqdm import tqdm
from label_studio_sdk import LabelStudio
from label_studio_sdk.converter import Converter
from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path

# ========================= CONFIG (CHANGE ONCE) =========================
LS_URL       = "http://localhost:8080"
API_KEY      = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA3MTkzOTkyNSwiaWF0IjoxNzY0NzM5OTI1LCJqdGkiOiJmZjljZTNmYzU0ODA0MzI5YTlkM2RiY2Q2YTMwOTcxZCIsInVzZXJfaWQiOiIyIn0.rLlywwxrA-2leLhEogT7vqwBUjoD9YzCJAYZ_B4DHeQ"
PROJECT_ID   = 10
OUTPUT_ROOT  = r"E:\MLOps\ls_dvc\data\exports"
# ======================================================================

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

def export_yolo():
    ls = LabelStudio(base_url=LS_URL, api_key=API_KEY)
    project = ls.projects.get(id=PROJECT_ID)
    log.info(f"Connected to project: {project.title}")

    # 1. Create and download export snapshot
    log.info("Creating export snapshot...")
    export = ls.projects.exports.create(PROJECT_ID, title="YOLO Full Export")
    while getattr(export, "status", "") == "in_progress":
        time.sleep(3)
        export = ls.projects.exports.get(id=PROJECT_ID, export_pk=export.id)

    data = ls.projects.exports.download(id=PROJECT_ID, export_pk=export.id, export_type="JSON")
    snapshot_path = os.path.join(OUTPUT_ROOT, f"project_{PROJECT_ID}_snapshot.json")
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    
    with open(snapshot_path, "wb") as f:
        for chunk in data:
            f.write(chunk)
    
    with open(snapshot_path) as f:
        tasks = json.load(f)
    log.info(f"Exported {len(tasks)} tasks → {snapshot_path}")

    # 2. Convert to YOLO format
    log.info("Converting to YOLO format...")
    converter = Converter(config=project.label_config, project_dir=OUTPUT_ROOT)
    yolo_dir = os.path.join(OUTPUT_ROOT, "yolo_dataset")
    converter.convert_to_yolo(snapshot_path, yolo_dir, is_dir=False)
    log.info(f"YOLO labels ready → {yolo_dir}/labels/")

    # 3. Download all images
    img_dir = os.path.join(yolo_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    log.info(f"Downloading {len(tasks)} images...")

    for task in tqdm(tasks, desc="Images"):
        url = next(iter(task["data"].values()))
        try:
            local_path = get_local_path(url, LS_URL, API_KEY, download_resources=True)
            filename = os.path.basename(local_path).split("__", 1)[-1]
            shutil.copy2(local_path, os.path.join(img_dir, filename))
        except Exception as e:
            log.warning(f"Failed {task['id']}: {e}")

    log.info(f"COMPLETE! Full YOLO dataset ready:\n   → {yolo_dir}")
    log.info(f"   Images : {len(os.listdir(img_dir))}")
    log.info(f"   Labels : {len([f for f in os.listdir(os.path.join(yolo_dir, 'labels')) if f.endswith('.txt')])}")

    # Auto-version with DVC
    os.system(f"dvc add {yolo_dir}")
    log.info("Dataset versioned with DVC → run 'dvc push' to save")

if __name__ == "__main__":
    import time
    time.sleep(1)  # nice terminal spacing
    export_yolo()