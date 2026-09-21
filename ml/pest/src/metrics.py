from __future__ import annotations

import numpy as np
import torch


def box_iou_np(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if len(a) == 0 or len(b) == 0:
        return np.zeros((len(a), len(b)), dtype=np.float32)
    lt = np.maximum(a[:, None, :2], b[None, :, :2])
    rb = np.minimum(a[:, None, 2:], b[None, :, 2:])
    wh = np.maximum(rb - lt, 0)
    inter = wh[..., 0] * wh[..., 1]
    area_a = np.maximum(a[:, 2] - a[:, 0], 0) * np.maximum(a[:, 3] - a[:, 1], 0)
    area_b = np.maximum(b[:, 2] - b[:, 0], 0) * np.maximum(b[:, 3] - b[:, 1], 0)
    return inter / np.maximum(area_a[:, None] + area_b[None, :] - inter, 1e-9)


def ap_from_pr(recall: np.ndarray, precision: np.ndarray) -> float:
    # COCO/VOC-style 101-point interpolation. At each recall level use the
    # maximum precision achieved for any recall >= that level.
    x = np.linspace(0.0, 1.0, 101)
    values = []
    for r in x:
        values.append(float(np.max(precision[recall >= r])) if np.any(recall >= r) else 0.0)
    return float(np.mean(values))


def evaluate_predictions(
    predictions: list[torch.Tensor | np.ndarray],
    targets: list[torch.Tensor | np.ndarray],
    num_classes: int,
) -> dict[str, float]:
    pred_np = [p.detach().cpu().numpy() if torch.is_tensor(p) else np.asarray(p) for p in predictions]
    gt_np = [t.detach().cpu().numpy() if torch.is_tensor(t) else np.asarray(t) for t in targets]

    thresholds = np.arange(0.50, 1.00, 0.05)
    areas = {
        "all": (0.0, float("inf")),
        "small": (0.0, 32.0 * 32.0),
        "medium": (32.0 * 32.0, 96.0 * 96.0),
        "large": (96.0 * 96.0, float("inf")),
    }

    aps = {name: [] for name in areas}
    precision50 = []
    recall50 = []

    for area_name, (amin, amax) in areas.items():
        for thr in thresholds:
            class_aps = []
            for cls in range(num_classes):
                records = []
                n_gt = 0
                for pi, (pred, gt) in enumerate(zip(pred_np, gt_np)):
                    if gt.size:
                        gt = gt.reshape(-1, 5)
                    else:
                        gt = np.empty((0, 5), dtype=np.float32)
                    if pred.size:
                        pred = pred.reshape(-1, 6)
                    else:
                        pred = np.empty((0, 6), dtype=np.float32)

                    gmask = gt[:, 0].astype(np.int64) == cls if len(gt) else np.zeros(0, dtype=bool)
                    g = gt[gmask, 1:5]
                    if len(g):
                        wh = g[:, 2:4] - g[:, 0:2]
                        ar = wh[:, 0] * wh[:, 1]
                        g = g[(ar >= amin) & (ar < amax)]
                    n_gt += len(g)

                    pmask = pred[:, 5].astype(np.int64) == cls if len(pred) else np.zeros(0, dtype=bool)
                    p = pred[pmask]
                    if len(p):
                        order = np.argsort(-p[:, 4])
                        p = p[order]
                    records.append((p, g))

                if n_gt == 0:
                    continue

                scores = []
                matches = []
                for p, g in records:
                    used = np.zeros(len(g), dtype=bool)
                    if len(p):
                        ious = box_iou_np(p[:, :4], g) if len(g) else np.zeros((len(p), 0), dtype=np.float32)
                        for j in range(len(p)):
                            scores.append(float(p[j, 4]))
                            if len(g):
                                k = int(np.argmax(ious[j]))
                                ok = ious[j, k] >= thr and not used[k]
                                matches.append(1 if ok else 0)
                                if ok:
                                    used[k] = True
                            else:
                                matches.append(0)

                if not scores:
                    class_aps.append(0.0)
                    continue
                order = np.argsort(-np.asarray(scores))
                tp = np.asarray(matches, dtype=np.float32)[order]
                fp = 1.0 - tp
                cum_tp = np.cumsum(tp)
                cum_fp = np.cumsum(fp)
                recall = cum_tp / max(n_gt, 1)
                precision = cum_tp / np.maximum(cum_tp + cum_fp, 1e-9)
                class_aps.append(ap_from_pr(recall, precision))

            aps[area_name].append(float(np.mean(class_aps)) if class_aps else 0.0)

    # Aggregate global precision/recall at IoU 0.50, all areas.
    total_tp = total_fp = total_gt = 0
    thr = 0.50
    for pred, gt in zip(pred_np, gt_np):
        pred = pred.reshape(-1, 6) if pred.size else np.empty((0, 6), dtype=np.float32)
        gt = gt.reshape(-1, 5) if gt.size else np.empty((0, 5), dtype=np.float32)
        total_gt += len(gt)
        used = np.zeros(len(gt), dtype=bool)
        order = np.argsort(-pred[:, 4]) if len(pred) else []
        for idx in order:
            same = np.where(gt[:, 0].astype(np.int64) == int(pred[idx, 5]))[0]
            if len(same):
                ious = box_iou_np(pred[idx:idx + 1, :4], gt[same, 1:5])[0]
                k = int(np.argmax(ious))
                gi = same[k]
                if ious[k] >= thr and not used[gi]:
                    total_tp += 1
                    used[gi] = True
                else:
                    total_fp += 1
            else:
                total_fp += 1
    total_fn = total_gt - total_tp
    precision = total_tp / max(total_tp + total_fp, 1)
    recall = total_tp / max(total_gt, 1)

    return {
        "precision": float(precision),
        "recall": float(recall),
        "mAP50": float(aps["all"][0]),
        "mAP50_95": float(np.mean(aps["all"])),
        "AP_small": float(np.mean(aps["small"])),
        "AP_medium": float(np.mean(aps["medium"])),
        "AP_large": float(np.mean(aps["large"])),
    }
