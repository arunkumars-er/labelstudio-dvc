**Label Studio SDK + DVC workflow**:

---

# Label Studio sdk + DVC ML Pipeline

This repository implements **two reproducible pipelines** using **Label Studio SDK** and **DVC**:

1. **Pre-annotation & Task Creation Pipeline**
2. **Annotation Export & Model Improvement Pipeline**

The goal is to close the loop between **model → annotation → retraining**.


---
## Project Structure

```text
.
├── .dvc/                   # DVC metadata
├── .venv_ls/               # Local virtual environment (not tracked)
├── data/
│   ├── raw/                # Raw input data (images, videos, etc.)
│   ├── exports/            # Label Studio exports
│   └── processed/          # Processed / training-ready data
├── models/
│   └── best.pt             # model for active learning(improve model)  
├── src/
│   └── labelstudio/
│       ├── configs/
│       │   ├── sam_segment.xml   # sam server(brush based RLE) Rectangle/keypoint label
│       │   └── yolo_preannotation.xml # yolo server (RectangleLabels)
│       ├── improve_model/
│       │   └── pre_annotate.py # active learning (add images for batch and preannotate)
│       ├── assign_task.py # use README inside here more detail
│       ├── create_task.py 
│       ├── export_task.py # use README inside here for more detail
|       └── README.md
├── dvc.yaml
├── requirements.txt
└── README.md
```

---
## Pipelines Overview

---

##  Pipeline 1: Pre-annotation & Task Creation

**Purpose:**
Automatically pre-annotate raw data using an ML model and push tasks to Label Studio.

### Flow

```
Raw Data → active learing(pre_annotate) → export task → train model → loop to maximum data
```

### Steps

1. **Create Label Studio tasks**
    create task with images in raw/ 

   ```bash
   python src/labelstudio/create_task.py
   ```
   start with small data → annotate it

2. **Pre-annotate data to bulk**

   * Uses a trained model (`models/best.pt`)
   * Generates predictions compatible with Label Studio

   ```bash
   python src/labelstudio/improve_model/pre_annotate.py
   ```

3. **Validate with human-in-loop**
4. **Train with same bulk data**

### Inputs

* `data/raw/`
* `models/best.pt`


---

##  Pipeline 2: Annotation Export & Model Improvement

**Purpose:**
Takes all images in raw/ and creates task and also assings the task with account available in labelstudio server.
### Flow

```
Label Studio → Create task → Assign task | export
```

### Steps

1. **Create Label Studio tasks**
    create task with images in raw/ 

   ```bash
   python src/labelstudio/create_task.py
   ```
   start with small data → annotate it

2. **Assign tasks to annotators**

   ```bash
   python src/labelstudio/assign_task.py
   ```
3. **Export completed tasks**

   ```bash
   python src/labelstudio/export_task.py
   ```


---

##  DVC Integration

DVC is used to:

* Track datasets (`data/`)
* Track model artifacts (`models/`)
* Reproduce pipelines


---

## Environment Variables

Set Label Studio credentials before running labelstudio:

```bash
export LABEL_STUDIO_URL=http://localhost:8080
export LABEL_STUDIO_API_KEY=your_api_key
```

---


