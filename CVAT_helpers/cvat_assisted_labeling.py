import PIL.Image
from ultralytics import YOLO

import cvat_sdk.auto_annotation as cvataa
import cvat_sdk.models as models

_model = YOLO(r"C:\Path\To\Trained\Model\best.pt")

spec = cvataa.DetectionFunctionSpec(
    labels=[cvataa.label_spec(name, id) for id, name in _model.names.items()],
)

def _yolo_to_cvat(results):
    for result in results:
        for box, label in zip(result.boxes.xyxy, result.boxes.cls):
            yield cvataa.rectangle(int(label.item()), [p.item() for p in box])

def detect(context, image):
    return list(_yolo_to_cvat(_model.predict(source=image, verbose=False)))
