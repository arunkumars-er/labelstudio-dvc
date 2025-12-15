**Label Studio SDK + DVC workflow**:

---

# Label Studio sdk + DVC ML Pipeline

This repository implements **two reproducible pipelines** using **Label Studio SDK** and **DVC**:

1. **Pre-annotation & Task Creation Pipeline**
2. **Annotation Export & Model Improvement Pipeline**

The goal is to close the loop between **model → annotation → retraining**.



## Pipelines Overview

---

##  Pipeline 1: Pre-annotation & Task Creation

**Purpose:**
Automatically pre-annotate raw data using an ML model and push tasks to Label Studio.

### Flow

```
Raw Data → Pre-annotation → Create Tasks → Assign Tasks
```

### Steps

1. **Pre-annotate data**

   * Uses a trained model (`models/best.pt`)
   * Generates predictions compatible with Label Studio

   ```bash
   python src/labelstudio/improve_model/pre_annotate.py
   ```

2. **Create Label Studio tasks**

   ```bash
   python src/labelstudio/create_task.py
   ```

3. **Assign tasks to annotators**

   ```bash
   python src/labelstudio/assign_task.py
   ```

### Inputs

* `data/raw/`
* `models/best.pt`

### Outputs

* Tasks created in Label Studio
* Pre-annotated predictions visible to annotators

---

##  Pipeline 2: Annotation Export & Model Improvement

**Purpose:**
Export completed annotations from Label Studio and prepare them for retraining.

### Flow

```
Label Studio → Export Annotations → Process Data → Retrain Model
```

### Steps

1. **Export completed tasks**

   ```bash
   python src/labelstudio/export_task.py
   ```

2. **Store exports**

   * Saved under:

     ```
     data/exports/
     ```

3. **Process annotations**

   * Convert Label Studio format → model training format
   * Stored in:

     ```
     data/processed/
     ```

4. **Retrain / improve model**

   * Output updated model to:

     ```
     models/
     ```

---

##  DVC Integration

DVC is used to:

* Track datasets (`data/`)
* Track model artifacts (`models/`)
* Reproduce pipelines


---

## Environment Variables

Set Label Studio credentials before running pipelines:

```bash
export LABEL_STUDIO_URL=http://localhost:8080
export LABEL_STUDIO_API_KEY=your_api_key
```

---

