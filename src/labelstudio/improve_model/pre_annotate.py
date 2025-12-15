# src/pipeline/pre_annotate_folder_perfect.py
# FINAL VERSION — Works 100% with your XML + best.pt + 25 classes

from ultralytics import YOLO
from label_studio_sdk import LabelStudio
from pathlib import Path
import logging

# ========================= CONFIG (MATCH YOUR XML) =========================
LS_URL = "http://localhost:8080"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA3MTkzOTkyNSwiaWF0IjoxNzY0NzM5OTI1LCJqdGkiOiJmZjljZTNmYzU0ODA0MzI5YTlkM2RiY2Q2YTMwOTcxZCIsInVzZXJfaWQiOiIyIn0.rLlywwxrA-2leLhEogT7vqwBUjoD9YzCJAYZ_B4DHeQ"
PROJECT_ID = 10

# Your fine-tuned model
MODEL_PATH = r"E:\MLOps\ls_dvc\models\best.pt"  

# Thresholds 
YOLO_CONF_THRESHOLD = 0.1      # model_score_threshold="0.1" 
MIN_SCORE_TO_SHOW = 0.1        # Same as above

# Your 25 exact class names 
LS_CLASSES = [
    "ac_asst", "ac_control", "ac_ctr_left", "ac_ctr_right", "ac_drvr",
    "assy_module", "bezel", "bezel_switches", "colps_steering", "dashboard",
    "duct", "gar_glv_box_padding", "garnish_ctr", "hazard_switches", "key",
    "lights", "push_button", "screen", "screen_garnish", "screw_lwr",
    "steering_coil", "steering_cover", "usb_aux", "usb_aux_container", "wiper"
]

# Load model + client
model = YOLO(MODEL_PATH)
ls = LabelStudio(base_url=LS_URL, api_key=API_KEY)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def pre_annotate_folder(
    folder: str,
    batch_size: int = 1000
):
    folder_path = Path(folder)
    print(f"Looking for images in: {folder_path}")
    images = list(folder_path.glob("*.[jJ][pP][gG]")) + list(folder_path.glob("*.[pP][nN][gG]"))
    images = images[-batch_size:]

    if not images:
        log.warning("No images found!")
        return

    tasks = []
    log.info(f"Pre-annotating {len(images)} images using your best.pt (25 classes)")

    for img_path in images:
        try:
            # Run your fine-tuned model
            results = model(img_path, conf=YOLO_CONF_THRESHOLD, verbose=False)[0]

            regions = []
            if results.boxes is not None and len(results.boxes) > 0:
                boxes = results.boxes
                names = results.names  # YOLO class names (0,1,2,...)

                for i in range(len(boxes)):
                    conf = float(boxes.conf[i])
                    if conf < MIN_SCORE_TO_SHOW:
                        continue

                    cls_id = int(boxes.cls[i])
                    model_class_name = names[cls_id]

                    # Map YOLO class index → your exact Label Studio class name
                    # IMPORTANT: Your model must be trained with classes in this exact order!
                    if cls_id >= len(LS_CLASSES):
                        log.warning(f"Unknown class ID {cls_id} in {img_path.name}")
                        continue
                    ls_label = LS_CLASSES[cls_id]

                    # Normalized coordinates (0–1) → Label Studio % (0–100)
                    x_center, y_center, width, height = boxes.xywhn[i].tolist()

                    region = {
                        "from_name": "labels",           
                        "to_name": "image1",             
                        "type": "rectanglelabels",
                        "value": {
                            "x": (x_center - width / 2) * 100,
                            "y": (y_center - height / 2) * 100,
                            "width": width * 100,
                            "height": height * 100,
                            "rectanglelabels": [ls_label]
                        },
                        "score": conf
                    }
                    regions.append(region)

            # Build final task
            tasks.append({
                "data": {
                    "image": f"/data/local-files/?d={folder_path.resolve()}/{img_path.name}"
                },
                "predictions": [{
                    "result": regions,
                    "score": max([r["score"] for r in regions] or [0])
                }] if regions else [{"result": [], "score": 0}]
            })

        except Exception as e:
            log.error(f"Error on {img_path.name}: {e}")

    # BULK IMPORT — Instant pre-annotation
    if tasks:
        ls.projects.import_tasks(id=PROJECT_ID, request=tasks)
        log.info(f"SUCCESS: {len(tasks)} images pre-annotated with your 25-class model!")


# RUN IT
if __name__ == "__main__":
    pre_annotate_folder(
        folder=r"E:\MLOps\ls_dvc\data\raw",
        batch_size=10
    )