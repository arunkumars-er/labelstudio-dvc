# Create_task.py-Label Studio Image Importer (Local Files, Duplicate-Safe) 

This script automates **creating or reusing a Label Studio project** and **importing local image files** into it **without duplicates**, using Label Studio’s **local-files serving** feature.

---

### Label Studio Configuration 

Label Studio **must** be configured to allow local files.

###  Set local-files root

This directory must be a **parent directory of your images**.


```bash
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=E:/MLOps
```

start label-studio

---

### Environment Variables 
- `LABEL_STUDIO_URL` (default: `http://localhost:8080`)
- `LABEL_STUDIO_API_KEY` (**required**)
- `LS_PROJECT_NAME` (default: `default_project`)
- `LS_DATA_KEY` (default: `image`)
- `LS_LABEL_CONFIG` (default: `sam_segment.xml`)
- `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT` (**required**)
---

### Folder Structure Example

```
E:/MLOps/
├── ls_dvc/
│   ├── data/
│   │   └── raw/
│   │       ├── img_001.jpg
│   │       ├── img_002.png
│   │       └── ...
│   └── src/
│       └── labelstudio/
│           └── create_import.py
```

---

### Usage

```bash
python src/labelstudio/create_import.py data/raw/
```

---

### Command-Line Arguments

| Argument    | Description                          |
| ----------- | ------------------------------------ |
| `folder`    | Folder containing images (recursive) |
| `--url`     | Label Studio URL                     |
| `--key`     | Label Studio API key                 |
| `--project` | Project name     (new or existing)   | 
| `--config`  | Label config XML file                |
| `--root`    | Local files root                     |

### Example with overrides

```bash
python create_import.py data/raw \
  --url http://localhost:8080 \
  --key YOUR_API_KEY \
  --project sam_segmentation \
  --config configs/sam_segment.xml \
  --root E:/MLOps
```

---

### Local File URL Format

Images are referenced like this:

```
/data/local-files/?d= E:/MLOps/ls_dvc/data/raw/image.jpg
```

This allows Label Studio to load files directly from disk without uploading them.


---

After completion:

```
http://localhost:8080/projects/<project_id>/data
```



---

# export_task.py

This script exports **fully annotated Label Studio projects** into a **ready-to-train YOLO dataset**

---

### What This Script Does

1. Connects to Label Studio
2. Creates an **export snapshot** of the project
3. Downloads tasks as JSON
4. Converts annotations to **YOLO format**
5. Downloads **all images** used in tasks
6. Builds a complete YOLO dataset:

   ```
   yolo_dataset/
   ├── images/
   └── labels/
   ```
7. Versions the dataset with **DVC**

---

### Configuration

Edit these  env variables at the top of the file:

```python
LS_URL      = "http://localhost:8080"
API_KEY    = "YOUR_LABEL_STUDIO_API_KEY"
PROJECT_ID = 10
OUTPUT_ROOT = r"E:\MLOps\ls_dvc\data\exports\yolo_full"
```

| Variable      | Description                       |
| ------------- | --------------------------------- |
| `LS_URL`      | Label Studio server URL           |
| `API_KEY`     | Label Studio API key              |
| `PROJECT_ID`  | Project ID to export              |
| `OUTPUT_ROOT` | Where the dataset will be created |

---

### Usage

From project root:

```bash
python src/labelstudio/export_to_yolo.py
```
---

### Output Structure

```
yolo_full/
├── project_10_snapshot.json
├── yolo_dataset/
│   ├── images/
│   │   ├── img_001.jpg
│   │   ├── img_002.jpg
│   │   └── ...
│   └── labels/
│       ├── img_001.txt
│       ├── img_002.txt
│       └── ...
└── yolo_dataset.dvc
```

---

### Label Format (YOLO)

Each label file contains:

```
<class_id> <x_center> <y_center> <width> <height>
```

All values are **normalized (0–1)**.

Class IDs are derived from the order of labels in your **Label Studio config XML**.

---

### Image Download Logic

* Images are resolved via `get_local_path`
* Works with:

  * Local-files
  * Uploaded images
  * Remote URLs
* Original filenames are preserved
* Cached images are reused when possible

---
### Export Format Available here
```md
- JSON
- JSON_MIN
- CSV
- TSV
- COCO
- COCO_WITH_IMAGES
- VOC
- YOLO
- YOLO_WITH_IMAGES
- YOLO_OBB
- YOLO_OBB_WITH_IMAGES
- BRUSH_TO_NUMPY
- BRUSH_TO_PNG
- BRUSH_TO_COCO
```
---