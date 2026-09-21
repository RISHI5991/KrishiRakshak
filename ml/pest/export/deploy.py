import argparse
import json
import torch
import torch.nn as nn
from pathlib import Path
from PIL import Image
import torchvision.transforms.functional as F_tv

from src.yolo26n import YOLO26n
from src.model import DhurandharM3
from src.student import StudentPestDetector

class PestDetectorAPI:
    """Inference API mapping to Requirement 24."""
    def __init__(self, model_path, arch='m3', num_classes=24, conf=0.25):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if arch == 'm3':
            self.model = DhurandharM3(num_classes, pretrained_backbone=False)
        elif arch == 'yolo26n':
            self.model = YOLO26n(num_classes)
        elif arch == 'student':
            self.model = StudentPestDetector(num_classes)
        else:
            raise ValueError(f"Unknown arch {arch}")
            
        ckpt = torch.load(model_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(ckpt.get('model_state_dict', ckpt))
        self.model.to(self.device)
        self.model.eval()
        
        self.conf = conf
        # PEST24 Classes mapping
        self.classes = [
            'Bollworm', 'Meadow borer', 'Gryllotalpa orientalis', 'Little Gecko', 
            'Agriotes fuscicollis Miwa', 'Nematode trench', 'Athetis lepigone', 
            'Scotogramma trifolii Rottemberg', 'Armyworm', 'Spodoptera cabbage', 
            'Anomala corpulenta', 'Spodoptera exigua', 'Plutella xylostella', 
            'holotrichia parallela', 'Rice planthopper', 'Yellow tiger', 
            'Land tiger', 'eight-character tiger', 'holotrichia oblita', 
            'Stem borer', 'Striped rice bore', 'Rice Leaf Roller', 
            'Spodoptera litura', 'Melahotus'
        ]

    def preprocess(self, image: Image.Image):
        # Letterbox to 640x640 or target size
        w, h = image.size
        sz = max(w, h)
        img_padded = Image.new("RGB", (sz, sz), (114, 114, 114))
        img_padded.paste(image, (0, 0))
        img_resized = img_padded.resize((640, 640), Image.BILINEAR)
        tensor = F_tv.to_tensor(img_resized).unsqueeze(0).to(self.device)
        return tensor, (sz/640, sz/640) # scaling factors

    @torch.no_grad()
    def predict(self, image: Image.Image):
        tensor, (sx, sy) = self.preprocess(image)
        outputs = self.model(tensor)
        
        # Format detections
        preds = self.model.head.predict_from_outputs(outputs, conf=self.conf, max_det=300)[0]
        
        detections = []
        for det in preds:
            x1, y1, x2, y2, conf, cls_id = det.tolist()
            cls_id = int(cls_id)
            detections.append({
                "class_id": cls_id,
                "class_name": self.classes[cls_id],
                "confidence": conf,
                "x1": x1 * sx,
                "y1": y1 * sy,
                "x2": x2 * sx,
                "y2": y2 * sy
            })
        return detections

def export_model(model, image_size, output_path, format="onnx"):
    model.eval()
    dummy_input = torch.randn(1, 3, image_size, image_size, device=next(model.parameters()).device)
    
    if format == "onnx":
        onnx_path = output_path.with_suffix('.onnx')
        torch.onnx.export(
            model, dummy_input, onnx_path,
            opset_version=12,
            input_names=['images'],
            output_names=['outputs'],
            dynamic_axes={'images': {0: 'batch'}, 'outputs': {0: 'batch'}}
        )
        print(f"Exported to {onnx_path}")
    else:
        raise NotImplementedError(f"Format {format} not implemented.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, required=True)
    parser.add_argument("--arch", type=str, default="m3")
    parser.add_argument("--export", action="store_true")
    args = parser.parse_args()
    
    if args.export:
        api = PestDetectorAPI(args.ckpt, arch=args.arch)
        export_model(api.model, 640, Path(args.ckpt))
    else:
        print("Use API via: `from scripts.deploy import PestDetectorAPI`")
