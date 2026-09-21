"""Export student model to ESP32-S3 deployable .h C file.

Pipeline: PyTorch → ONNX → TFLite (INT8 quantized) → C header array

Usage:
    python scripts/export_esp32.py --checkpoint checkpoints/student_best.pt
    python scripts/export_esp32.py --checkpoint checkpoints/student_best.pt --image-size 192
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pest_ml.src.student import StudentPestDetector

PEST24_CLASSES = [
    "Bollworm", "Meadow borer", "Gryllotalpa orientalis", "Little Gecko",
    "Agriotes fuscicollis Miwa", "Nematode trench", "Athetis lepigone",
    "Scotogramma trifolii Rottemberg", "Armyworm", "Spodoptera cabbage",
    "Anomala corpulenta", "Spodoptera exigua", "Plutella xylostella",
    "holotrichia parallela", "Rice planthopper", "Yellow tiger",
    "Land tiger", "eight-character tiger", "holotrichia oblita",
    "Stem borer", "Striped rice bore", "Rice Leaf Roller",
    "Spodoptera litura", "Melahotus",
]


def export_onnx(model: torch.nn.Module, img_size: int, out_path: Path) -> Path:
    """Export PyTorch model to ONNX."""
    model.eval()
    dummy = torch.randn(1, 3, img_size, img_size)
    onnx_path = out_path.with_suffix(".onnx")

    # We need to trace through the model and only export the backbone + head forward
    # not the dict output. Let's wrap it.
    class ExportWrapper(torch.nn.Module):
        def __init__(self, m):
            super().__init__()
            self.backbone = m.backbone
            self.head_cls = m.head.cls_heads
            self.head_box = m.head.box_heads

        def forward(self, x):
            feats = self.backbone(x)
            outs = []
            for feat, cls_h, box_h in zip(feats, self.head_cls, self.head_box):
                outs.append(box_h(feat))
                outs.append(cls_h(feat))
            # Return flat tuple: box0, cls0, box1, cls1, box2, cls2
            return tuple(outs)

    wrapper = ExportWrapper(model)
    wrapper.eval()

    output_names = []
    for i in range(3):
        output_names.extend([f"boxes_{i}", f"scores_{i}"])

    torch.onnx.export(
        wrapper, dummy, str(onnx_path),
        opset_version=12,
        input_names=["images"],
        output_names=output_names,
        dynamic_axes=None,  # Fixed size for MCU
    )
    print(f"ONNX exported: {onnx_path} ({onnx_path.stat().st_size / 1024:.1f} KB)")
    return onnx_path


def export_tflite_int8(onnx_path: Path, img_size: int, out_path: Path) -> Path:
    """Convert ONNX to TFLite with full INT8 quantization."""
    import tensorflow as tf

    # Method: ONNX → TF SavedModel → TFLite
    # Using tf.lite converter with representative dataset for INT8
    try:
        import onnx
        from onnx_tf.backend import prepare
        onnx_model = onnx.load(str(onnx_path))
        tf_rep = prepare(onnx_model)
        saved_model_dir = str(out_path.parent / "student_savedmodel")
        tf_rep.export_graph(saved_model_dir)
    except ImportError:
        # Fallback: use onnx2tf if onnx-tf not available
        import subprocess
        saved_model_dir = str(out_path.parent / "student_savedmodel")
        subprocess.run([
            sys.executable, "-m", "onnx2tf",
            "-i", str(onnx_path),
            "-o", saved_model_dir,
            "--non_verbose",
        ], check=True)

    # Convert to TFLite with INT8 quantization
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Representative dataset for calibration
    def representative_dataset():
        for _ in range(100):
            data = np.random.uniform(0, 1, (1, img_size, img_size, 3)).astype(np.float32)
            yield [data]

    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()
    tflite_path = out_path.with_suffix(".tflite")
    tflite_path.write_bytes(tflite_model)
    print(f"TFLite INT8 exported: {tflite_path} ({tflite_path.stat().st_size / 1024:.1f} KB)")
    return tflite_path


def tflite_to_c_header(tflite_path: Path, out_path: Path, var_name: str = "pest_model_data") -> Path:
    """Convert TFLite binary to C header file (like xxd -i)."""
    data = tflite_path.read_bytes()
    h_path = out_path.with_suffix(".h")

    lines = []
    lines.append(f"// Auto-generated from {tflite_path.name}")
    lines.append(f"// Model: Dhurandhar StudentPestDetector for ESP32-S3")
    lines.append(f"// Classes: 24 (Pest24)")
    lines.append(f"// Input: 192x192x3 UINT8")
    lines.append(f"// Size: {len(data)} bytes")
    lines.append(f"//")
    lines.append(f"// Class mapping:")
    for i, cls in enumerate(PEST24_CLASSES):
        lines.append(f"//   {i:2d}: {cls}")
    lines.append(f"")
    lines.append(f"#ifndef PEST_MODEL_DATA_H")
    lines.append(f"#define PEST_MODEL_DATA_H")
    lines.append(f"")
    lines.append(f"#include <stdint.h>")
    lines.append(f"")
    lines.append(f"const unsigned int {var_name}_len = {len(data)};")
    lines.append(f"alignas(16) const unsigned char {var_name}[] = {{")

    # Write hex data in rows of 12 bytes
    for i in range(0, len(data), 12):
        chunk = data[i:i+12]
        hex_vals = ", ".join(f"0x{b:02x}" for b in chunk)
        if i + 12 < len(data):
            hex_vals += ","
        lines.append(f"    {hex_vals}")

    lines.append(f"}};")
    lines.append(f"")
    lines.append(f"#endif // PEST_MODEL_DATA_H")

    h_path.write_text("\n".join(lines))
    print(f"C header exported: {h_path} ({h_path.stat().st_size / 1024:.1f} KB)")
    return h_path


def export_direct_c_header(model: torch.nn.Module, out_path: Path) -> Path:
    """Direct PyTorch weights → C header (fallback if TFLite pipeline unavailable).
    
    Exports all weights as const arrays for manual C inference engine.
    """
    h_path = out_path.with_suffix(".h")
    lines = []
    lines.append("// Dhurandhar StudentPestDetector — Direct Weight Export")
    lines.append("// For ESP32-S3 with custom C inference engine")
    lines.append("// Classes: 24 (Pest24), Input: 192x192x3")
    lines.append("")
    lines.append("#ifndef PEST_MODEL_WEIGHTS_H")
    lines.append("#define PEST_MODEL_WEIGHTS_H")
    lines.append("")
    lines.append("#include <stdint.h>")
    lines.append("")

    total_bytes = 0
    for name, param in model.state_dict().items():
        arr = param.detach().cpu().numpy().flatten()
        # Quantize to INT8
        scale = max(abs(arr.max()), abs(arr.min())) / 127.0
        if scale == 0:
            scale = 1.0
        q = np.clip(np.round(arr / scale), -128, 127).astype(np.int8)

        safe_name = name.replace(".", "_")
        lines.append(f"// {name}: shape={list(param.shape)}, scale={scale:.8f}")
        lines.append(f"const float {safe_name}_scale = {scale:.8f}f;")
        lines.append(f"const int {safe_name}_len = {len(q)};")
        lines.append(f"const int8_t {safe_name}[] = {{")

        for i in range(0, len(q), 16):
            chunk = q[i:i+16]
            hex_vals = ", ".join(str(v) for v in chunk)
            if i + 16 < len(q):
                hex_vals += ","
            lines.append(f"    {hex_vals}")

        lines.append("};")
        lines.append("")
        total_bytes += len(q)

    lines.append(f"// Total model size: {total_bytes} bytes ({total_bytes/1024:.1f} KB)")
    lines.append("")
    lines.append("#endif // PEST_MODEL_WEIGHTS_H")

    h_path.write_text("\n".join(lines))
    print(f"Direct C header exported: {h_path} ({h_path.stat().st_size / 1024:.1f} KB)")
    return h_path


def main():
    parser = argparse.ArgumentParser(description="Export student model to ESP32-S3 .h file")
    parser.add_argument("--checkpoint", type=Path, default=None, help="Student model checkpoint")
    parser.add_argument("--image-size", type=int, default=192)
    parser.add_argument("--output-dir", type=Path, default=Path("pest_ml/export"))
    parser.add_argument("--method", choices=["tflite", "direct", "both"], default="both")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Build model
    model = StudentPestDetector(24)
    if args.checkpoint and args.checkpoint.exists():
        ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
        model.load_state_dict(ckpt.get("model_state_dict", ckpt))
        print(f"Loaded checkpoint: {args.checkpoint}")
    else:
        print("WARNING: No checkpoint loaded, using random weights (for pipeline testing)")

    model.eval()
    params = sum(p.numel() for p in model.parameters())
    print(f"Student model: {params:,} params")
    print(f"Input size: {args.image_size}x{args.image_size}")

    out_base = args.output_dir / "pest_detector_esp32"

    if args.method in ("tflite", "both"):
        try:
            onnx_path = export_onnx(model, args.image_size, out_base)
            tflite_path = export_tflite_int8(onnx_path, args.image_size, out_base)
            tflite_to_c_header(tflite_path, out_base)
            print("\n=== TFLite INT8 → .h export COMPLETE ===")
        except Exception as e:
            print(f"\nTFLite pipeline failed: {e}")
            print("Falling back to direct export...")
            if args.method == "tflite":
                args.method = "direct"

    if args.method in ("direct", "both"):
        direct_path = args.output_dir / "pest_detector_weights"
        export_direct_c_header(model, direct_path)
        print("\n=== Direct C header export COMPLETE ===")

    # Summary
    print("\n" + "=" * 60)
    print("ESP32-S3 DEPLOYMENT SUMMARY")
    print("=" * 60)
    print(f"Parameters      : {params:,}")
    print(f"INT8 model size : ~{params / 1024:.0f} KB")
    print(f"Input           : {args.image_size}x{args.image_size}x3 (UINT8)")
    print(f"Activations     : ReLU6 only (no SiLU/Softplus)")
    print(f"Box decode      : ReLU (no exp/log)")
    print(f"Output          : 24 classes, per-grid box+class")
    print(f"ESP32-S3 Flash  : {'FITS' if params < 500000 else 'TOO LARGE'}")
    print(f"ESP32-S3 PSRAM  : {'FITS' if params < 2000000 else 'TOO LARGE'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
