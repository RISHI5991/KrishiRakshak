from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass
class BranchLoss:
    total: torch.Tensor
    box: torch.Tensor
    cls: torch.Tensor
    positives: int


class M3Loss:
    """Small-target-aware, candidate-restricted anchor-free loss.

    The implementation is deliberately explicit and self-contained:
    - P2/P3/P4 candidate points.
    - Center sampling with size-aware level eligibility.
    - Task-alignment ranking only over local candidates.
    - One-to-many top-k supervision and one-to-one top-1 supervision.
    - Direct LTRB regression (DFL-free) with IoU + normalized SmoothL1.
    - Quality-weighted focal BCE to avoid the huge-negative problem of plain BCE.

    Assignment is non-differentiable, as it should be; box/class losses are
    fully differentiable through the selected predictions.
    """

    def __init__(
        self,
        num_classes: int = 24,
        image_size: int = 640,
        topk: int = 10,
        center_radius: float = 2.5,
        small_max: float = 32.0,
        medium_max: float = 96.0,
        box_weight: float = 7.5,
        cls_weight: float = 2.5,  # Increased from 1.0 based on data (classification needs more gradient)
        one2one_weight: float = 1.0,
        focal_gamma: float = 2.5, # Increased from 2.0 to aggressively push down easy negatives
        focal_alpha: float = 0.75,
        strides: tuple[int, ...] = (4, 8, 16),
        decode_mode: str = "softplus",
    ) -> None:
        self.nc = num_classes
        self.image_size = image_size
        self.topk = topk
        self.center_radius = center_radius
        self.small_max = small_max
        self.medium_max = medium_max
        self.box_weight = box_weight
        self.cls_weight = cls_weight
        self.one2one_weight = one2one_weight
        self.focal_gamma = focal_gamma
        self.focal_alpha = focal_alpha
        self.strides = strides
        self.decode_mode = decode_mode

        point_levels = []
        point_strides = []
        point_tensors = []
        for level, stride in enumerate(self.strides):
            h = image_size // stride
            w = image_size // stride
            y, x = torch.meshgrid(
                torch.arange(h, dtype=torch.float32),
                torch.arange(w, dtype=torch.float32),
                indexing="ij",
            )
            pts = torch.stack(
                ((x + 0.5) * stride, (y + 0.5) * stride),
                dim=-1,
            ).reshape(-1, 2)
            point_tensors.append(pts)
            point_levels.append(torch.full((pts.shape[0],), level, dtype=torch.long))
            point_strides.append(torch.full((pts.shape[0],), stride, dtype=torch.float32))

        self.points_cpu = torch.cat(point_tensors, dim=0)
        self.levels_cpu = torch.cat(point_levels, dim=0)
        self.strides_cpu = torch.cat(point_strides, dim=0)

    @staticmethod
    def box_iou(boxes1: torch.Tensor, boxes2: torch.Tensor) -> torch.Tensor:
        if boxes1.numel() == 0 or boxes2.numel() == 0:
            return boxes1.new_zeros((boxes1.shape[0], boxes2.shape[0]))
        lt = torch.maximum(boxes1[:, None, :2], boxes2[None, :, :2])
        rb = torch.minimum(boxes1[:, None, 2:], boxes2[None, :, 2:])
        wh = (rb - lt).clamp(min=0)
        inter = wh[..., 0] * wh[..., 1]
        area1 = ((boxes1[:, 2] - boxes1[:, 0]).clamp(min=0) *
                 (boxes1[:, 3] - boxes1[:, 1]).clamp(min=0))
        area2 = ((boxes2[:, 2] - boxes2[:, 0]).clamp(min=0) *
                 (boxes2[:, 3] - boxes2[:, 1]).clamp(min=0))
        union = area1[:, None] + area2[None, :] - inter
        return inter / union.clamp(min=1e-7)

    @staticmethod
    def ciou_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        px = (pred[:, 0] + pred[:, 2]) * 0.5
        py = (pred[:, 1] + pred[:, 3]) * 0.5
        tx = (target[:, 0] + target[:, 2]) * 0.5
        ty = (target[:, 1] + target[:, 3]) * 0.5
        pw = (pred[:, 2] - pred[:, 0]).clamp(min=1e-6)
        ph = (pred[:, 3] - pred[:, 1]).clamp(min=1e-6)
        tw = (target[:, 2] - target[:, 0]).clamp(min=1e-6)
        th = (target[:, 3] - target[:, 1]).clamp(min=1e-6)

        iou = M3Loss.box_iou(pred, target).diag().clamp(0.0, 1.0)
        rho2 = (px - tx).pow(2) + (py - ty).pow(2)

        enclose_x1 = torch.minimum(pred[:, 0], target[:, 0])
        enclose_y1 = torch.minimum(pred[:, 1], target[:, 1])
        enclose_x2 = torch.maximum(pred[:, 2], target[:, 2])
        enclose_y2 = torch.maximum(pred[:, 3], target[:, 3])
        c2 = ((enclose_x2 - enclose_x1).pow(2) +
              (enclose_y2 - enclose_y1).pow(2)).clamp(min=1e-6)

        v = (4.0 / torch.pi**2) * (
            torch.atan(tw / th) - torch.atan(pw / ph)
        ).pow(2)
        with torch.no_grad():
            alpha = v / (1.0 - iou + v).clamp(min=1e-6)
        ciou = iou - (rho2 / c2 + alpha * v)
        return (1.0 - ciou).clamp(min=0.0, max=2.0)

    def _decode_level(
        self,
        box_logits: torch.Tensor,
        level: int,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # box_logits: [B,4,H,W]
        b, _, h, w = box_logits.shape
        stride = self.strides[level]
        points = self._points_for(level, box_logits.device, box_logits.dtype)
        
        raw_dist = box_logits.permute(0, 2, 3, 1)
        if self.decode_mode == "relu":
            distances = F.relu(raw_dist).reshape(b, -1, 4) * stride
        else:
            distances = F.softplus(raw_dist).reshape(b, -1, 4) * stride
            
        centers = points.unsqueeze(0)
        decoded = torch.stack(
            [
                centers[..., 0] - distances[..., 0],
                centers[..., 1] - distances[..., 1],
                centers[..., 0] + distances[..., 2],
                centers[..., 1] + distances[..., 3],
            ],
            dim=-1,
        )
        return decoded, points, torch.full((h * w,), stride, device=box_logits.device, dtype=box_logits.dtype)

    def _points_for(self, level: int, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
        mask = self.levels_cpu == level
        return self.points_cpu[mask].to(device=device, dtype=dtype)

    def _eligible_levels(self, gt: torch.Tensor) -> tuple[int, ...]:
        w = float((gt[2] - gt[0]).clamp(min=1.0))
        h = float((gt[3] - gt[1]).clamp(min=1.0))
        m = max(w, h)
        if m <= self.small_max:
            return (0,)
        if m <= self.medium_max:
            return (0, 1)
        return (0, 1, 2)

    def _assign_one(
        self,
        pred_boxes: torch.Tensor,
        pred_scores: torch.Tensor,
        targets: torch.Tensor,
        topk: int,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Assign one image. Only local candidate points enter IoU/ranking."""
        n = pred_boxes.shape[0]
        device = pred_boxes.device
        assigned_gt = torch.full((n,), -1, dtype=torch.long, device=device)
        assigned_quality = torch.zeros((n,), dtype=pred_boxes.dtype, device=device)

        if targets.numel() == 0:
            return assigned_gt, assigned_quality

        points = self.points_cpu.to(device=device, dtype=pred_boxes.dtype)
        levels = self.levels_cpu.to(device=device)
        strides = self.strides_cpu.to(device=device, dtype=pred_boxes.dtype)
        probs = pred_scores.sigmoid()

        for gi in range(targets.shape[0]):
            gt = targets[gi, 1:5]
            cls = int(targets[gi, 0].item())
            allowed = self._eligible_levels(gt)

            level_mask = torch.zeros(n, dtype=torch.bool, device=device)
            for level in allowed:
                level_mask |= levels == level

            cx = (gt[0] + gt[2]) * 0.5
            cy = (gt[1] + gt[3]) * 0.5
            radius = self.center_radius * strides
            center_mask = ((points[:, 0] - cx).abs() <= radius) & ((points[:, 1] - cy).abs() <= radius)
            inside = (
                (points[:, 0] >= gt[0]) & (points[:, 0] <= gt[2]) &
                (points[:, 1] >= gt[1]) & (points[:, 1] <= gt[3])
            )
            candidate = level_mask & (center_mask | inside)
            ids = torch.where(candidate)[0]

            if ids.numel() == 0:
                allowed_ids = torch.where(level_mask)[0]
                dist2 = (points[allowed_ids, 0] - cx).pow(2) + (points[allowed_ids, 1] - cy).pow(2)
                ids = allowed_ids[dist2.argmin()].view(1)

            cand_boxes = pred_boxes[ids]
            ious = self.box_iou(cand_boxes, gt.view(1, 4)).squeeze(1)
            cls_prob = probs[ids, cls]
            alignment = cls_prob.clamp(min=1e-6).pow(0.5) * ious.clamp(min=1e-6).pow(2.0)

            k = min(topk, ids.numel())
            values, order = torch.topk(alignment, k=k, largest=True)
            chosen = ids[order]

            for li, pi in enumerate(chosen):
                q = values[li].detach()
                if q > assigned_quality[pi]:
                    assigned_gt[pi] = gi
                    assigned_quality[pi] = q

        return assigned_gt, assigned_quality

    def _branch_loss(
        self,
        boxes_by_level: list[torch.Tensor],
        scores_by_level: list[torch.Tensor],
        targets: list[torch.Tensor],
        topk: int,
    ) -> BranchLoss:
        device = boxes_by_level[0].device
        batch = boxes_by_level[0].shape[0]

        decoded_levels = []
        score_levels = []
        for li in range(3):
            decoded, _, _ = self._decode_level(boxes_by_level[li], li)
            decoded_levels.append(decoded)
            score_levels.append(
                scores_by_level[li].permute(0, 2, 3, 1).reshape(batch, -1, self.nc)
            )

        pred_boxes_all = torch.cat(decoded_levels, dim=1)
        pred_scores_all = torch.cat(score_levels, dim=1)
        points = self.points_cpu.to(device=device, dtype=pred_boxes_all.dtype)
        point_strides = self.strides_cpu.to(device=device, dtype=pred_boxes_all.dtype)

        total_box = torch.zeros((), device=device)
        total_cls = torch.zeros((), device=device)
        total_pos = 0

        for bi in range(batch):
            pred_boxes = pred_boxes_all[bi]
            pred_scores = pred_scores_all[bi]
            target = targets[bi].to(device)

            assigned_gt, _ = self._assign_one(
                pred_boxes.detach(),
                pred_scores.detach(),
                target,
                topk,
            )

            positive = assigned_gt >= 0
            pos_idx = torch.where(positive)[0]
            target_cls = torch.zeros_like(pred_scores)

            if pos_idx.numel():
                gt_idx = assigned_gt[pos_idx]
                cls_idx = target[gt_idx, 0].long()
                gt_pos = target[gt_idx, 1:5]
                pred_pos = pred_boxes[pos_idx]

                pos_iou = self.box_iou(
                    pred_pos.detach(),
                    gt_pos,
                ).diag().detach().clamp(0, 1)
                target_cls[pos_idx, cls_idx] = pos_iou

                pos_points = points[pos_idx]
                pos_stride = point_strides[pos_idx]
                target_dist = torch.stack(
                    [
                        pos_points[:, 0] - gt_pos[:, 0],
                        pos_points[:, 1] - gt_pos[:, 1],
                        gt_pos[:, 2] - pos_points[:, 0],
                        gt_pos[:, 3] - pos_points[:, 1],
                    ],
                    dim=1,
                ).clamp(min=0)
                pred_dist = torch.stack(
                    [
                        pos_points[:, 0] - pred_pos[:, 0],
                        pos_points[:, 1] - pred_pos[:, 1],
                        pred_pos[:, 2] - pos_points[:, 0],
                        pred_pos[:, 3] - pos_points[:, 1],
                    ],
                    dim=1,
                ).clamp(min=0)

                norm_target = target_dist / pos_stride[:, None]
                norm_pred = pred_dist / pos_stride[:, None]
                l1 = F.smooth_l1_loss(norm_pred, norm_target, reduction="none").mean(dim=1)
                ciou = self.ciou_loss(pred_pos, gt_pos)
                weights = pos_iou.detach().clamp(min=0.05)
                total_box = total_box + ((0.5 * l1 + 0.5 * ciou) * weights).sum() / weights.sum().clamp(min=1e-6)
                total_pos += int(pos_idx.numel())

            prob = pred_scores.sigmoid()
            bce = F.binary_cross_entropy_with_logits(pred_scores, target_cls, reduction="none")
            negative_weight = self.focal_alpha * prob.pow(self.focal_gamma)
            weight = torch.where(target_cls > 0, target_cls, negative_weight)
            normalizer = (target_cls > 0).sum().detach().clamp(min=1).to(bce.dtype)
            total_cls = total_cls + (bce * weight).sum() / normalizer

        denom = max(batch, 1)
        total_box = total_box / denom
        total_cls = total_cls / denom
        total = self.box_weight * total_box + self.cls_weight * total_cls
        return BranchLoss(total, total_box.detach(), total_cls.detach(), total_pos)

    def __call__(self, outputs, targets: list[torch.Tensor]) -> dict[str, object]:
        many = outputs["one2many"]
        one = outputs["one2one"]

        lm = self._branch_loss(many["boxes"], many["scores"], targets, self.topk)
        lo = self._branch_loss(one["boxes"], one["scores"], targets, 1)

        total = lm.total + self.one2one_weight * lo.total
        return {
            "loss": total,
            "box_loss": lm.box + self.one2one_weight * lo.box,
            "cls_loss": lm.cls + self.one2one_weight * lo.cls,
            "positive_assignments": lm.positives + lo.positives,
        }
