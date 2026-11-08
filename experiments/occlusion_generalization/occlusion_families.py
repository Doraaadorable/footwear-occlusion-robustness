"""Held-out occlusion and degradation families for the Handiprint models.

The occlusion-augmented heads were trained with white rectangles
(``severe_mask`` in the Handiprint notebook). This module defines other
corruptions so the evaluation can check whether the augmentation benefit
carries over to occluders the model never saw during training.

Images are float arrays in [0, 1] on a white canvas: 1.0 is paper, lower
values are ink. ``box`` is (top, left, bottom, right) of the resized
impression inside the canvas.
"""
from __future__ import annotations

import zlib

import numpy as np
from scipy import ndimage as ndi

# Removal families hide part of the impression. Level = target fraction
# of the impression box that is covered.
REMOVAL_LEVELS = (0.40, 0.60, 0.80)

# Degradation families change the whole impression without hiding a region.
DEGRADATION_LEVELS = {
    "fade": (0.50, 0.30, 0.15),    # fraction of original ink contrast kept
    "noise": (0.10, 0.20, 0.30),   # Gaussian noise standard deviation
    "blur": (1.0, 2.0, 4.0),       # Gaussian blur sigma in pixels
}

# rect_white is the training family; all others are held out.
FAMILIES = {
    "rect_white": "removal",
    "blob_white": "removal",
    "stripes_white": "removal",
    "partial_contact": "removal",
    "rect_dark": "removal",
    "rect_texture": "removal",
    "fade": "degradation",
    "noise": "degradation",
    "blur": "degradation",
}
TRAINING_FAMILY = "rect_white"


def levels_for(family):
    if FAMILIES[family] == "removal":
        return REMOVAL_LEVELS
    return DEGRADATION_LEVELS[family]


def make_rng(seed, key, family, level, draw):
    """Seeded per image, family, level and draw so both models see the same mask."""
    return np.random.default_rng([
        int(seed),
        zlib.crc32(str(key).encode()),
        zlib.crc32(family.encode()),
        int(round(float(level) * 1000)),
        int(draw),
    ])


def _rect(box, frac, rng):
    """Same rectangle rule as the notebook's severe_mask (area = frac of box)."""
    top, left, bottom, right = box
    h, w = bottom - top, right - left
    rel_h = float(np.exp(rng.uniform(np.log(frac), 0.0)))
    rel_w = frac / rel_h
    mh = max(1, min(h, int(round(rel_h * h))))
    mw = max(1, min(w, int(round(rel_w * w))))
    y0 = top + int(rng.integers(0, h - mh + 1))
    x0 = left + int(rng.integers(0, w - mw + 1))
    mask = np.zeros((h, w), dtype=bool)
    mask[y0 - top:y0 - top + mh, x0 - left:x0 - left + mw] = True
    return mask


def _blob(box, frac, rng):
    """Irregular blob(s): top-frac pixels of a smoothed random field."""
    top, left, bottom, right = box
    h, w = bottom - top, right - left
    sigma = max(2.0, 0.08 * min(h, w))
    field = ndi.gaussian_filter(rng.standard_normal((h, w)), sigma)
    threshold = np.quantile(field, 1.0 - frac)
    return field >= threshold


def _stripes(box, frac, rng):
    """Parallel bands at a random angle covering about frac of the box."""
    top, left, bottom, right = box
    h, w = bottom - top, right - left
    angle = rng.uniform(0, np.pi)
    period = rng.uniform(0.15, 0.35) * min(h, w)
    phase = rng.uniform(0, period)
    yy, xx = np.mgrid[0:h, 0:w]
    coord = xx * np.cos(angle) + yy * np.sin(angle) + phase
    return np.mod(coord, period) < frac * period


def _partial_contact(box, frac, rng):
    """Remove one end of the impression (toe or heel) as if contact was partial."""
    top, left, bottom, right = box
    h, w = bottom - top, right - left
    cut = max(1, int(round(frac * h)))
    mask = np.zeros((h, w), dtype=bool)
    if rng.random() < 0.5:
        mask[:cut] = True
    else:
        mask[h - cut:] = True
    return mask


_MASKS = {
    "rect_white": _rect,
    "blob_white": _blob,
    "stripes_white": _stripes,
    "partial_contact": _partial_contact,
    "rect_dark": _rect,
    "rect_texture": _rect,
}


def apply_family(canvas, box, family, level, rng):
    """Return (corrupted image, info) for one image.

    ``info`` records the realised area fraction and the fraction of the
    impression's ink that was removed or altered inside the mask.
    """
    x = np.asarray(canvas, dtype=np.float32).copy()
    top, left, bottom, right = box
    sub = x[top:bottom, left:right]
    ink = 1.0 - sub
    total_ink = float(ink.sum())
    info = {"family": family, "level": float(level),
            "area_fraction": 0.0, "ink_coverage": 0.0}

    if FAMILIES[family] == "removal":
        mask = _MASKS[family](box, float(level), rng)
        info["area_fraction"] = float(mask.mean())
        info["ink_coverage"] = float(ink[mask].sum() / max(total_ink, 1e-6))
        if family == "rect_dark":
            # A dark occluder with mild texture: unlike white masks, it is
            # not the same colour as paper.
            fill = np.clip(0.15 + 0.05 * rng.standard_normal(mask.sum()), 0, 1)
            sub[mask] = fill
        elif family == "rect_texture":
            # Substrate-like texture (debris, tile grain) over the region.
            noise = ndi.gaussian_filter(rng.standard_normal(sub.shape), 1.5)
            noise = (noise - noise.min()) / max(np.ptp(noise), 1e-6)
            texture = 0.35 + 0.65 * noise
            sub[mask] = texture[mask]
        else:
            sub[mask] = 1.0
        x[top:bottom, left:right] = sub
    elif family == "fade":
        x = 1.0 - (1.0 - x) * float(level)
    elif family == "noise":
        region = x[top:bottom, left:right]
        region += float(level) * rng.standard_normal(region.shape).astype(np.float32)
        x[top:bottom, left:right] = region
    elif family == "blur":
        x = ndi.gaussian_filter(x, float(level))
    else:
        raise KeyError(family)
    return np.clip(x, 0.0, 1.0).astype(np.float32), info


def corrupt_split(canvases, boxes, keys, family, level, draw, seed):
    """Corrupt every image in a split for one draw."""
    images, infos = [], []
    for canvas, box, key in zip(canvases, boxes, keys):
        rng = make_rng(seed, key, family, level, draw)
        image, info = apply_family(canvas, box, family, level, rng)
        images.append(image)
        infos.append({"key": key, "draw": int(draw), **info})
    return np.stack(images), infos


# ---------------------------------------------------------------- metrics

def pair_bootstrap_weights(pair_ids, labels, n_boot, seed):
    """Image weights for a bootstrap that resamples whole pairs within class.

    Mirrors make_weights in the Handiprint notebook: both images of a pair
    share one multiplicity, and class pair counts stay fixed.
    """
    pair_ids = np.asarray(pair_ids)
    labels = np.asarray(labels)
    pairs, first = np.unique(pair_ids, return_index=True)
    pair_class = labels[first]
    rng = np.random.default_rng(seed)
    wp = np.zeros((n_boot, len(pairs)))
    groups = [np.flatnonzero(pair_class == c) for c in np.unique(pair_class)]
    for b in range(n_boot):
        for idx in groups:
            drawn = rng.choice(idx, size=len(idx), replace=True)
            wp[b] += np.bincount(drawn, minlength=len(pairs))
    index = np.searchsorted(pairs, pair_ids)
    return wp[:, index]


def weighted_balanced_accuracy(y, yhat, weights):
    """Balanced accuracy for each row of ``weights`` (shape B x N)."""
    y = np.asarray(y).astype(int)
    correct = (np.asarray(yhat).astype(int) == y).astype(float)
    weights = np.atleast_2d(weights)
    recalls = []
    for c in (0, 1):
        w = weights * (y == c)
        recalls.append((w * correct).sum(1) / np.maximum(w.sum(1), 1e-12))
    return 0.5 * (recalls[0] + recalls[1])


def summarise(scores_by_model, y, weights, ci=(2.5, 97.5), reference="original"):
    """Point estimate, interval and paired difference versus ``reference``.

    ``scores_by_model`` maps a model name to an array (draws x images) of
    Nike probabilities. Balanced accuracy is averaged across draws inside
    each bootstrap replicate, as in the original extension.
    """
    point_w = np.ones((1, weights.shape[1]))
    rows, boot = [], {}
    for name, scores in scores_by_model.items():
        yhat = (np.asarray(scores) > 0.5).astype(int)
        point = np.mean([weighted_balanced_accuracy(y, d, point_w)[0] for d in yhat])
        draws = np.stack([weighted_balanced_accuracy(y, d, weights) for d in yhat])
        boot[name] = draws.mean(0)
        lo, hi = np.percentile(boot[name], ci)
        rows.append({"model": name, "balanced_accuracy": float(point),
                     "ci_low": float(lo), "ci_high": float(hi)})
    diffs = []
    for name in scores_by_model:
        if name == reference:
            continue
        delta = boot[name] - boot[reference]
        point = ([r for r in rows if r["model"] == name][0]["balanced_accuracy"]
                 - [r for r in rows if r["model"] == reference][0]["balanced_accuracy"])
        lo, hi = np.percentile(delta, ci)
        diffs.append({"model": name, "reference": reference,
                      "delta_balanced_accuracy": float(point),
                      "ci_low": float(lo), "ci_high": float(hi)})
    return rows, diffs


def evaluate(models_by_name, score_fn, canvases, boxes, keys, y, pair_ids,
             seed, draws, n_boot, families=None):
    """Run every family and level; return metric, difference and prediction rows.

    ``score_fn(models, images)`` returns one Nike probability per image.
    """
    families = list(FAMILIES) if families is None else list(families)
    weights = pair_bootstrap_weights(pair_ids, y, n_boot, seed + 1)
    metric_rows, diff_rows, pred_rows, mask_rows = [], [], [], []

    # Clean baseline, computed once.
    clean = np.stack([np.asarray(c, dtype=np.float32) for c in canvases])
    scores = {m: np.atleast_2d(score_fn(ms, clean)) for m, ms in models_by_name.items()}
    rows, diffs = summarise(scores, y, weights)
    for r in rows:
        metric_rows.append({"family": "clean", "held_out": False, "level": 0.0, **r})
    for d in diffs:
        diff_rows.append({"family": "clean", "held_out": False, "level": 0.0, **d})

    for family in families:
        for level in levels_for(family):
            batches = []
            for k in range(draws):
                images, infos = corrupt_split(canvases, boxes, keys, family, level, k, seed)
                batches.append(images)
                mask_rows.extend(infos)
            scores = {}
            for name, models in models_by_name.items():
                scores[name] = np.stack([score_fn(models, b) for b in batches])
                for k in range(draws):
                    for key, pid, yt, s in zip(keys, pair_ids, y, scores[name][k]):
                        pred_rows.append({"family": family, "level": float(level),
                                          "draw": k, "model": name, "key": key,
                                          "pair_id": pid, "y_true": int(yt),
                                          "score_nike": float(s)})
            rows, diffs = summarise(scores, y, weights)
            held_out = family != TRAINING_FAMILY
            for r in rows:
                metric_rows.append({"family": family, "held_out": held_out,
                                    "level": float(level), **r})
            for d in diffs:
                diff_rows.append({"family": family, "held_out": held_out,
                                  "level": float(level), **d})
    return metric_rows, diff_rows, pred_rows, mask_rows
