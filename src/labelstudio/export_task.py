from label_studio_sdk import LabelStudio
import os

# -----------------------------
# CONFIG
# -----------------------------
LS_URL = "http://localhost:8080"
API_KEY = "YOUR_API_KEY"  
PROJECT_ID = 25
IMAGE_DIR = "/home/arun-er/Documents/ls_dvc/data/raw"
OUTPUT_ZIP = f"/home/arun-er/Documents/ls_dvc/exports/project_{PROJECT_ID}_brush_coco.zip"

# -----------------------------
# INIT
# -----------------------------
client = LabelStudio(base_url=LS_URL, api_key=API_KEY)

print("\n=== STEP 1: Create Import Storage ===")

storage = client.import_storage.local.create(
    project=PROJECT_ID,
    path=IMAGE_DIR,
    title="Local Raw Images",
    regex_filter=".*\\.(jpg|png|jpeg)$",
    use_blob_urls=True     
)

print(f"Created Import Storage ID: {storage.id}")

print("\n=== STEP 2: Sync Import Storage (load images into LS backend) ===")
sync_result = client.import_storage.local.sync(id=storage.id)
print("Sync result:", sync_result)

print("\n=== STEP 3: Export Project in BRUSH_TO_COCO format ===")
print("Available export formats:")
formats = client.projects.exports.list_formats(id=PROJECT_ID)
for f in formats:
    print(" →", f)

export_type = "BRUSH_TO_COCO"

print(f"\nRequested export type: {export_type}")

# Export as binary stream
bytestream = client.projects.exports.as_binary(
    project_id=PROJECT_ID,
    export_type=export_type
)

# Write ZIP file
print(f"\nSaving export to: {OUTPUT_ZIP}")
os.makedirs(os.path.dirname(OUTPUT_ZIP), exist_ok=True)

with open(OUTPUT_ZIP, "wb") as f:
    f.write(bytestream)

print("\n Export completed successfully!")
print(f" File saved → {OUTPUT_ZIP}")

# ------------------------------
# OPTIONAL: VERIFY ZIP CONTENTS
# ------------------------------
import zipfile

print("\n=== STEP 4: Verify ZIP ===")
with zipfile.ZipFile(OUTPUT_ZIP, "r") as zipf:
    names = zipf.namelist()

    img_files = [n for n in names if "images/" in n]
    ann_files = [n for n in names if "annotations/" in n]

    print(f"Images found: {len(img_files)}")
    print(f"Annotations found: {len(ann_files)}")

    if len(img_files) == 0:
        print(" ERROR: No images exported — check import storage again.")
    else:
        print(" Images exported correctly.")

print("\n=== DONE ===\n")
