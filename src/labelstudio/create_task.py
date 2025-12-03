
# # create_import.py ← FINAL VERSION THAT WORKS 100%

# import os
# import sys
# import argparse
# from pathlib import Path
# from label_studio_sdk import LabelStudio

# # ==================== CONFIG ====================
# LABEL_STUDIO_URL = "http://localhost:8080"
# API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA3MTkzOTkyNSwiaWF0IjoxNzY0NzM5OTI1LCJqdGkiOiJmZjljZTNmYzU0ODA0MzI5YTlkM2RiY2Q2YTMwOTcxZCIsInVzZXJfaWQiOiIyIn0.rLlywwxrA-2leLhEogT7vqwBUjoD9YzCJAYZ_B4DHeQ"
# PROJECT_TITLE = "new"
# DATA_KEY = "image"
# LABEL_CONFIG_PATH = r"E:\MLOps\ls_dvc\src\labelstudio\configs\sam_segment.xml"
# # ===============================================

# client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)


# def load_label_config(path: str) -> str:
#     with open(path, "r") as f:
#         return f.read()

# LABEL_CONFIG = load_label_config(LABEL_CONFIG_PATH)

# def find_or_create_project():
#     print(f"Looking for project: '{PROJECT_TITLE}'...")
#     projects = client.projects.list()

#     for proj in projects:
#         if proj.title == PROJECT_TITLE:
#             print(f"Found existing project → ID = {proj.id}")
#             return proj.id

#     print("Creating new project...")
#     project = client.projects.create(
#         title=PROJECT_TITLE,
#         label_config=LABEL_CONFIG,
#         enable_empty_annotation=True,
#         show_instruction=True,
#         expert_instruction="Use SAM (click / Alt+click) → refine with Brush → Submit"
#     )
#     print(f"Project created! ID = {project.id}")
#     return project.id


# def import_images(folder_path, project_id):
#     folder = Path(folder_path)
#     if not folder.exists():
#         print(f"Folder not found: {folder}")
#         return

#     supported = {"*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.webp"}
#     images = []
#     for pattern in supported:
#         images.extend(folder.rglob(pattern))

#     if not images:
#         print("No images found!")
#         return

#     print(f"Found {len(images)} images → creating local-files URLs...")
#     # document_root = os.getenv('LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT', '/home/arun-er').rstrip('/')
#     document_root = os.getenv('LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT', 'E:/MLOps').rstrip('/')

#     tasks = []
#     for img_path in images:
#         full_path = img_path.as_posix()
#         print(full_path)

#         if full_path.startswith(document_root):
#             rel_path = full_path[len(document_root):].lstrip('/')
#         else:
#             rel_path = full_path.lstrip('/')

#         # ls_url = f"/data/local-files/?d=Documents/ls_dvc/{img_path}"
#         ls_url = f"/data/local-files/?d=ls_dvc/{img_path}"
#         tasks.append({"data": {DATA_KEY: ls_url}})
#         print(f"→ {ls_url}")

#     print(f"Uploading {len(tasks)} tasks...")

#     try:
#         client.projects.import_tasks(id=project_id, request=tasks)
#         print(f"SUCCESS! Imported {len(tasks)} images!")
#     except Exception as e:
#         print(f"Import failed: {e}")


# def import_images_without_duplicates(folder_path, project_id):
#     folder = Path(folder_path)

#     supported = {"*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.webp"}
#     new_files = []
#     for pattern in supported:
#         new_files.extend(folder.rglob(pattern))

#     print(f"Found {len(new_files)} images in folder.")

#     existing_tasks = list(client.tasks.list(project=project_id))
#     existing_urls = set()

#     for t in existing_tasks:
#         if t.data and "image" in t.data:
#             existing_urls.add(t.data["image"])

#     print(f"Existing tasks in LS: {len(existing_urls)}")

#     base = Path("E:/MLOps/ls_dvc").resolve().as_posix()

#     tasks_to_import = []
#     for img in new_files:
#         img_posix = img.as_posix()
#         img_url = f"/data/local-files/?d=E:/MLOps/ls_dvc/{img_posix}"
#         print(f"Processing: {img_url}")
#         if img_url in existing_urls:
#             print(f"Skipping duplicate: {img_url}")
#             continue
#         tasks_to_import.append({"data": {"image": img_url}})

#     if not tasks_to_import:
#         print("No new images to import! All are duplicates.")
#         return

#     print(f"Importing {len(tasks_to_import)} new images...")
#     client.projects.import_tasks(id=project_id, request=tasks_to_import)
#     print("✓ Import completed without duplicates.")


# def main():
#     parser = argparse.ArgumentParser(description="Create project + import images (WORKS 100%)")
#     parser.add_argument("folder", help="Path to folder with images")
#     parser.add_argument("--url", default=LABEL_STUDIO_URL, help="Label Studio URL")
#     parser.add_argument("--key", default=API_KEY, help="API key")
#     args = parser.parse_args()

#     global client
#     client = LabelStudio(base_url=args.url, api_key=args.key)

#     project_id = find_or_create_project()

#     # import_images(args.folder, project_id)
#     import_images_without_duplicates(args.folder, project_id)

#     print("\n" + "="*80)
#     print("ALL DONE! Your project is ready and images WILL load:")
#     print(f"→ {args.url}/projects/{project_id}/data")
#     print("="*80)
#     print("Your annotators can start labeling NOW!")


# if __name__ == "__main__":
#     if len(sys.argv) == 1:
#         print("Usage: python create_import.py /path/to/images")
#         sys.exit(1)
#     main()

# # python src/labelstudio/create_import.py data/raw/


import os
import sys
import argparse
from pathlib import Path
from label_studio_sdk import LabelStudio


# ==================================================
# Load config from environment variables
# ==================================================
LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
PROJECT_TITLE = os.getenv("LS_PROJECT_NAME", "default_project")
DATA_KEY = os.getenv("LS_DATA_KEY", "image")
LABEL_CONFIG_PATH = os.getenv("LS_LABEL_CONFIG", "E:/MLOps/ls_dvc/src/labelstudio/configs/sam_segment.xml")
LOCAL_FILES_ROOT = os.getenv("LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT")
# ==================================================


# ==================================================
# Utilities
# ==================================================
def ensure_local_files_root():
    """Ensure the local-files root exists and is configured."""
    global LOCAL_FILES_ROOT

    if not LOCAL_FILES_ROOT:
        print("\n[ERROR] LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT is NOT set.")
        print("Label Studio cannot load local-files without this path.\n")
        print("Set it like this:\n")
        print("Linux/macOS:")
        print("    export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/path/to/data\n")
        print("Windows PowerShell:")
        print('    setx LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT "E:/MLOps"\n')
        sys.exit(1)

    root_path = Path(LOCAL_FILES_ROOT)

    if not root_path.exists():
        print(f"\n[ERROR] LOCAL_FILES_ROOT does not exist on this system:\n{LOCAL_FILES_ROOT}")
        sys.exit(1)

    LOCAL_FILES_ROOT = root_path.resolve().as_posix()
    print(f"[ROOT] Using LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT = {LOCAL_FILES_ROOT}")


def load_label_config(path: str) -> str:
    if not path:
        print("[WARNING] No label config provided.")
        return ""
    if not Path(path).exists():
        print(f"[WARNING] Label config file not found: {path}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def make_ls_local_file_url(path: Path) -> str:
    """
    Convert a real filesystem path into a Label Studio local-file URL.
    Example:
        LOCAL_FILES_ROOT = "E:/MLOps"
        file = "E:/MLOps/ls_dvc/data/raw/cat.jpg"
        output = "/data/local-files/?d=ls_dvc/data/raw/cat.jpg"
    """
    absolute = path.resolve().as_posix()

    if absolute.startswith(LOCAL_FILES_ROOT):
        rel = absolute[len(LOCAL_FILES_ROOT):].lstrip("/")
    else:
        print(f"[WARNING] Path is outside LOCAL_FILES_ROOT: {absolute}")
        rel = absolute

    return f"/data/local-files/?d=E:/MLOps/{rel}"


# ==================================================
# Project Management
# ==================================================
def find_or_create_project(client, label_config):
    print(f"Searching for project: '{PROJECT_TITLE}'...")
    projects = client.projects.list()

    for p in projects:
        if p.title == PROJECT_TITLE:
            print(f"[FOUND] Existing project ID = {p.id}")
            return p.id

    print("[INFO] Creating new project...")
    project = client.projects.create(
        title=PROJECT_TITLE,
        label_config=label_config,
        enable_empty_annotation=True,
        show_instruction=True,
        expert_instruction="Use SAM clicks + refine with Brush → Submit",
    )
    print(f"[CREATED] Project ID = {project.id}")
    return project.id


# ==================================================
# Import Logic (Duplicate-safe)
# ==================================================
def import_images_without_duplicates(folder_path, client, project_id):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"[ERROR] Image folder not found: {folder}")
        return

    supported = {"*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.webp"}
    new_files = []
    for pattern in supported:
        new_files.extend(folder.rglob(pattern))

    print(f"[INFO] Found {len(new_files)} images in folder.")

    # Get existing tasks from LS
    existing_tasks = list(client.tasks.list(project=project_id))
    existing_urls = {
        t.data.get(DATA_KEY)
        for t in existing_tasks
        if t.data and DATA_KEY in t.data
    }

    print(f"[INFO] Existing tasks in project: {len(existing_urls)}")

    tasks_to_import = []

    for img in new_files:
        ls_url = make_ls_local_file_url(img)

        if ls_url in existing_urls:
            print(f"[SKIP] Duplicate: {ls_url}")
            continue

        tasks_to_import.append({"data": {DATA_KEY: ls_url}})
        print(f"[ADD] {ls_url}")

    if not tasks_to_import:
        print("[INFO] No new images to import.")
        return

    print(f"[UPLOAD] Importing {len(tasks_to_import)} new images...")
    client.projects.import_tasks(id=project_id, request=tasks_to_import)
    print("[SUCCESS] Import completed!")


# ==================================================
# Main Entry
# ==================================================
def main():
    parser = argparse.ArgumentParser(description="Generic Label Studio Image Importer")
    parser.add_argument("folder", help="Folder containing images")
    parser.add_argument("--url", help="Label Studio URL")
    parser.add_argument("--key", help="API key", default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA3MTkzOTkyNSwiaWF0IjoxNzY0NzM5OTI1LCJqdGkiOiJmZjljZTNmYzU0ODA0MzI5YTlkM2RiY2Q2YTMwOTcxZCIsInVzZXJfaWQiOiIyIn0.rLlywwxrA-2leLhEogT7vqwBUjoD9YzCJAYZ_B4DHeQ")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--config", help="Label config XML file")
    parser.add_argument("--root", help="Local files root")
    args = parser.parse_args()

    global LABEL_STUDIO_URL, API_KEY, PROJECT_TITLE, LABEL_CONFIG_PATH, LOCAL_FILES_ROOT

    # Override with arguments
    LABEL_STUDIO_URL = args.url or LABEL_STUDIO_URL
    API_KEY = args.key or API_KEY
    PROJECT_TITLE = args.project or PROJECT_TITLE
    LABEL_CONFIG_PATH = args.config or LABEL_CONFIG_PATH
    LOCAL_FILES_ROOT = args.root or LOCAL_FILES_ROOT

    if not API_KEY:
        print("ERROR: API key missing. Set LABEL_STUDIO_API_KEY or use --API key.")
        sys.exit(1)

    ensure_local_files_root()

    client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)

    label_config = load_label_config(LABEL_CONFIG_PATH)
    project_id = find_or_create_project(client, label_config)

    import_images_without_duplicates(args.folder, client, project_id)

    print("\n" + "=" * 80)
    print("ALL DONE! Label Studio project is ready.")
    print(f"Open: {LABEL_STUDIO_URL}/projects/{project_id}/data")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python create_import.py /path/to/images")
        sys.exit(1)
    main()
# python src/labelstudio/create_import.py data/raw/